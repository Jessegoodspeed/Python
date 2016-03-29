import glossary
import random
import time
import builtins


def starts_lowercase_regex(name):
    """return True if starts with lowercase letter"""
    import re
    return re.match('[a-z]', name)

def starts_lowercase_string(name):
    """returns True if starts with lowercase letter"""
    import string
    return any(name.startswith(c) for c in string.ascii_lowercase)


starts_lowercase = starts_lowercase_string

def create_data():
    """return a dictionary of answers: definitions"""
    data_dict = {}
    for name in dir(builtins):
        if starts_lowercase(name):
            builtin_function = getattr(builtins, name)
            doc = builtin_function.__doc__
            if doc is not None:
                placeholder = '*' * len(name) 
                newdoc =  placeholder.join(doc.split(name)) 
                data_dict[name] = newdoc
    return data_dict


DATA = create_data()

def ask_question(definition, answer):
    """takes definition and answer, quizzes user, returns success (bool)"""
    time.sleep(.5)
    print('Tell me what name is associated with the following definition:')
    print(definition)
    response = input('> ')
    success = response == answer
    if success:
    	print('right!')
    else:
    	print('wrong!')
    return success


def main():
    attempts = successes = 0
    keys = list(DATA)
    random.shuffle(keys)
    for answer in keys:
        definition = DATA[answer] #glossary.CONCEPTS[answer]
        try: 
            success = ask_question(definition, answer)
        except EOFError:    	
            break
        attempts += 1
        if success:
    	    successes += 1
    total = len(keys)
    final_message ='{successes}/{total} right! {attempts} attempts'.format(successes=successes, total=total, attempts=attempts) 
    print(final_message)    
    results_file_name = 'results.log'
    open_file = open(results_file_name, 'a')
    with open_file as file_:
         file_.write(final_message + '\n')



if __name__ == '__main__':
    main()
