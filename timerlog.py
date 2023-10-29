
## Creating a decorator function
# func is the function we want to compute execution time
from functools import wraps
from collections import Counter
import re 
import string
import time
import pandas as pd
import plotly.express as px

filename = 'shakespeare.txt'

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs): 
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result, total_time #return the actual result of the function and its execution time
    return timeit_wrapper


@timeit
def dictCount_Words(filename):
    # create a list 
    punctuation_pattern = f"[{re.escape(string.punctuation)}]"
    dict_count = dict()
    # readfile
    with open(filename, mode='r') as f :
        content = f.read()
        content = re.sub(punctuation_pattern, '', content) # replace all kind of punctuation by a space inside our document
        words = content.split() # create a list containing each word from the document by splitting on spaces
        # Iterate through the words inside the list
        for word in words:
            # convert to lowercase for case-insensitive counting.
            word = word.lower()

            # If the word is in the dictionary, increment its count; otherwise, add it to the dictionary.
            if word in dict_count:
                dict_count[word] += 1
            else:
                dict_count[word] = 1

    return dict_count

@timeit
def dict_withCounter(filename):
    punctuation_pattern = f"[{re.escape(string.punctuation)}]"
    dict_Count = Counter()
    with open(filename, mode='r') as f :
        content = f.read()
        content = re.sub(punctuation_pattern, '', content)
        words = content.split()
        # Iterate through the words and update the counter
        for word in words:
            # convert to lowercase for case-insensitive counting
            word = word.lower()
            dict_Count[word]+=1
    
    return dict_Count

def plot_benchmarks(iter=10):
    withCounter = []
    withDict = []
    i=0
    while i< iter:
        result, execution_time = dict_withCounter('shakespeare.txt')
        withCounter.append(execution_time)
        result, execution_time = dictCount_Words('shakespeare.txt')
        withDict.append(execution_time)
        i+=1
    data = {
    'Iteration': range(1, iter + 1),
    'withCounter': withCounter,
    'withDict': withDict
}
    df = pd.DataFrame(data)
    fig = px.line(df, x='Iteration', y=['withCounter', 'withDict'], title='Execution Time Comparison')
    fig.update_xaxes(title_text='Iteration')
    fig.update_yaxes(title_text='Execution Time (seconds)')
    fig.show()
    return df

df = plot_benchmarks()


print('mean with counter : ', df['withCounter'].mean(), '\nvariance : ', df['withCounter'].var())
print('mean with dict : ', df['withDict'].mean(), '\nvariance : ', df['withDict'].var())

## using Counter execution time is longer, because it is based on dict object but it adds some other functionnalities that require more time during computation