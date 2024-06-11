default_prompt = """
Variables:
expenses: {0}
budget: {1}
country: {2}

PROVIDED VARIABLES ITS ALL INFORMATION THAT WE HAVE ABOUT USER THAT WANT TO ASK YOU SOMETHING

user request: {3}

GIVE RESPONSE IN THIS FORMAT (do with each category with unnecessary expenses):
    Name of expenses category: Short summary about expenses. Advices to optimize
"""