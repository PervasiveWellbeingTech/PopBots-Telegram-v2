from glob import glob
from os.path import join
import yaml
import utils
import random


class ShallowBot:
    """
    An object for the shallow bots 
    """

    def __init__(self, path):
        """
        Loads a yaml file for the bot
        """
        with open(path) as f:
            from_yaml =  yaml.safe_load(f)
            self.name = from_yaml.get('name', '')
            self.id = from_yaml.get('id', None)
            self.states = from_yaml['states']

        self.defaults = {}
        self.defaults['__yes__'] = ['yes', 'ok', 'sure', 'right', 'yea', 'ye', 'yup', 'yeah', 'okay']
        self.defaults['__no__'] = ['no', 'not',  'neither', 'neg', 'don\'t', 'doesn\'', 'donnot', 'dont', '\'t', 'nothing', 'nah', 'na']
        self.defaults['__dk__']= ["dk", "dunno", "dno", "don't know", "idk"]
        self.defaults['__greetings__'] = ['hi','hey', 'hello']

    def get_response(self, user_id:int, query:str, user_state, **kwargs):
        """
        This function returns a set of strings or
        commands given the input string and states.

        This function is meant to be called by the state handler

        Parameters:
            user_id(int) -- unser unique identifyer
            query (string) -- user input
            user_state -- The user's current state
            user_name(str) -- name of the user (what would the bot call them.)

        Returns
            Responses (list) -- list of all responses
            new_bot_state (str) -- new state of the user
        """
        if user_state == None: #if user state is unknown
            new_state = 'bot_opening' 
        else:
            prev_bot_state = user_state 
            new_state = self.get_next(prev_bot_state, query)

        if new_state:
            response = []

            #if there are multiple versions, select one at random.
            for res in self.states[new_state]['response']:
                if isinstance(res, list):
                    res = random.choice(res)
                response.append(res)

            return new_state, response, self.states[new_state].get('buttons', None)
        else:
            return None,[], None



    def get_next(self, prev_state:str, query:str):
        """
        This function gets the next state given the user input.

        Parameters:
            prev_state (dict) -- The previous state
            query(string) -- user input

        Assumptions:
            This assumes that yaml loaded dictionaries preserve order (python >= 3.6).
        """
        next_dict = self.states[prev_state]['next']
        if next_dict == None:
            return None
        elif isinstance(next_dict, dict):
            next_id = None
            for keywords, value in next_dict.items(): #NOTE: make sure dict preserves order
                if keywords == "__fallback__": #if it is fall back, permit everything.
                    next_id = value
                    break
                elif keywords in self.defaults and self.find_keyword(query, self.defaults[keywords]):
                    if keywords != "__no__" or (len(query.split(" ")) <= 5 and len(query) <= 25):
                        next_id = value
                        break
                elif self.find_keyword(query, keywords.split('|')):
                    print(query, keywords)
                    next_id = value
                    break
            assert next_id != None, "No dialog option match." #### fix
            return next_id
        elif isinstance(next_dict, str):
            return next_dict
        else:
            raise ValueError

    def find_keyword(self,input_str, word_list):
        """
        Loops through each word in the input string.
        Returns true is there is a match.

        Parameters:
            input_str (string) -- input string by the user
            word_list (list/tuple) -- list of extract_keywords_from_text

        Returns:
            (boolean) -- if keyword is found.
        """
        input_str = input_str.lower()
        return any([str(each) in str(input_str).split() for each in word_list])


    def replace_entities(self, responses, user_id, bot_id):
        """
        Replaces entity place holders such as {name} {bot_name} 
        with appropriate names

        Parameters:
            responses(list) -- list of text responses
            user_id(int) -- user unique identifyer
            bot_id(int) -- id of the bot 

        Returns:
            (list) -- list of strings the responses 
        """
        name = self.user_name_dict.get(user_id, '')
        problem = self.user_problem_dict.get(user_id, 'that')
        for res in responses:
            yield res.format(name=name, problem=problem)
    

##########################################################



def all_shallow_bots(folder):
    """
    Gets a list of all the shalllow bots in the folder.
    Parameter
        folder(string) -- name of the folder
    """
    bots = []
    folder_path = join(folder,'*.yaml')
    for bot_path in glob(folder_path):
        bots.append(ShallowBot(bot_path))
    return bots


if __name__ == '__main__':
    """
    Unit test.
    Looks at the names of all bots in the folder
    """

    testbot = ShallowBot('./shallow_bots/bot.yaml')
    print(testbot.get_response(10000, 'yes', ('Example Bot','end')))

