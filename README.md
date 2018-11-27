# BlocksWorldPlanner

The goal of this project was to implement a program that allows users to solve the blocks world problem interacting only using the natural language. Using the program the user has only to type sentences (reasonables in the domain of interest) that can be assertions, queries or commands. 
Once entered a sentence, the program recognize what kind it is and react accordingly to the result. In order to recognize the type of sentence the program uses the Natural Language Processing (NLP), a branch of AI that helps computers understand, interpret and manipulate human language. 
Indeed the program uses a Python library for NLP, namely Natural Language Toolkit (NLTK) [http://www.nltk.org/]. 
This library allows to build Python programs which work with human language data, providing text processing for classification, tokenization, tagging and parsing. Once the user has entered the sentence, the program takes, tokenizes and transforms it in a part-of- speech tagged tree structure. Once obtained the tagged tree structure of the entered sentence, the program explores it in order to understand what the user wants. 
Therefore it can act differently according to the cases. In case of an assertion, the program has to add facts from it to the knowledge base, according to the Planner Algorithm, while in case of a query it has to answer it according to the knowledge base. 
Instead in case of a command it has to run the planner algorithm in order to reach the required goal. All those actions have been implemented using another Python library, namely PySWIP [https://github.com/yuce/pyswip], a Python - SWI-Prolog bridge enabling to query SWI-Prolog in Python programs. The use of this library was necessary due to the decision of use Prolog in order to implement the Planner Algorithm. 
When an assertion is entered by the user, the program uses PySWIP in order to add new identified facts to the SWI-Prolog knowledge base, while when a query is entered, always using PySWIP the program forwards the correct equivalent query to SWI-Prolog interpreter, so it can answer correctly according to the current knowledge base. Instead when a command is requested by the user, it is transformed into a goal to reach and the execution of the Planner is required through PySWIP in order to reach this goal. 
Once the Planner has performed the needed actions, the user is informed of the new situation. 
The program is able to process lots of sentences, provided that they are correct in the domain of interest. 
The only constraint is that proper nouns (e.g. B, C) must start in upper case and that the sentence has to be simple, meaning that the program is not able to process for instance a sentence like “the block B is on the table, while the block C is red and is on the block B”. 

Here a list of tested sentences which can be used (terms in [] are optional): 

Assertions: 
- [the] [block] B is blue 
- [the] [red] [block] B is on the table 
- [the] [red] [block] B is on [the] [green] [block] C 
- there is a [red] block B on the table 
- there is a [red] block B on the [green] block C 
- B is blue 

Queries: 
- is B a [red] block? 
- is [the] [block] B red? 
- Is [the] [red] [block] B on the table? 
- Is [the] [green] [block] C on [the] [red] [block] B? 

Commands: 
- Put [the] [green] [block] C on the table 
- Put [the] [green] [block] C on [the] [red] [block] B 
- move the [green] block C on [the] [red] [block] B 
- shift the [green] block C on [the] [red] [block] B
