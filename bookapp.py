import re
import traceback

from bookdb import BookDB

DB = BookDB()

# Any request for the root of the application will map to the list page
# URL for book with key 'id1':  "http:\\localhost:8080/book/id1/"

def book(book_id):
    page = """
<h1>{title}</h1>
<table>
    <tr><th>Author</th><td>{author}</td></tr>
    <tr><th>Publisher</th><td>{publisher}</td></tr>
    <tr><th>ISBN</th><td>{isbn}</td></tr>
</table>
<a href="/">Back to the list</a>
"""
    book = DB.title_info(book_id)
    if book is None:
        raise NameError
    return page.format(**book)



def books():
    # Call all the books from the Book Database Model
    all_books = DB.titles()
    # Create the Main HTML Body
    body = ['<h1>My Bookshelf</h1>', '<ul>']
    # Create a template for book presentation
    item_template = '<li><a href="/book/{id}">{title}</a></li>'
    # Format all books in the List from the model
    for book in all_books:
        body.append(item_template.format(**book))
    body.append('</ul>')
    # Joing the text of information
    return '\n'.join(body)

def resolve_path(path):
    """
    Takes the path of the URI as an argument and returns the
    intended function to exectue and any additional 
    arguments that need be passed
    """

    # Create a dictionary that associates the 
    # URI Path to a function
    funcs = {
        '':books,
        'book':book,
    }

    # This will strip the provided path of it's right most
    # '/' and then split it on the remaining '/'
    path = path.strip('/').split('/')

    # Slice the list for the base function and arguments
    func_name = path[0]
    args = path[1:]

    # Find the name of the function corresponding to the URI 
    # and is available in the function dictionary
    try:
        func = funcs[func_name]
    # Exception where function is not available in the program. 
    except KeyError:
        raise NameError

    # Return the intended function and arguments
    return func, args


def application(environ, start_response):
    #status = "200 OK"
    #headers = [('Content-type', 'text/html')]
    #start_response(status, headers)
    #return ["<h1>No Progress Yet</h1>".encode('utf8')]
    # Define the HTTP Headers
    headers = [('Content-Type', 'text/html')]

    try:
        # Retrieve the URI from the Environment
        path = environ.get('PATH_INFO', None)

        # Case Statement to Handle No Path Info Passed
        if path is None:
            raise NameError
        # Retrieve the arguments and function via 'resolve_path'
        func, args = resolve_path(path)
        # Create the body of content by passing arguments
        # to desired function
        body = func(*args)
        # Provide a 200 Status Code
        status = "200 OK"
    # Case Statement to Handle a Name Error
    except NameError:
        status = "404 Not Found"
        body = '<h1> Not Found </h1>'
    # Handles any other Kind of Error
    except Exception:
        status = "500 Internal Server Error"
        body = '<h1>Internal Server Error</h1>'
        print(traceback.format_exc())
    # With everything passed, return the information
    finally:
        # Append the Headers
        headers.append(('Content-Length', str(len(body))))
        start_response(status, headers)
        return [body.encode('utf-8')]
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
