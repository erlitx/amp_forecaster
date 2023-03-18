import functools

#
# def simple_decorator(func):
#     def wrapper(*args, **kwargs):
#         return func(*args, **kwargs)
#     return wrapper
#
# @simple_decorator
# def greet_person(**kwargs):
#     name = kwargs.get("name", "NOT FOUND")
#     age = kwargs.get("age")
#     print(f"Hello, {name}!")
#
#     if age:
#         print(f"You are {age} years old.")
#
# dc = {"name": "Bob", "age": 25, "world": "Earth"}
# greet_person(**dc)



# def some_wrap(func):
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         if len(args) == 2:
#             print(f"{func.__name__} function is OK. Two args passed")
#             result = func(*args, **kwargs)
#             return result
#         else:
#             print(f"{func.__name__} function need to pass 2 args")
#             print(type(args))
#             pass
#     return wrapper
#
#
# @some_wrap
# def mest(nums):
#     """This is a test function"""
#     # print(f"==================================\n def test(a, b): \n args: [{a} and {b}]\n"
#     #       f"==================================")
#
#     return sum(nums)
#
# list = [1, 2, 3]
# result = mest(list)
# print(result)
# print(mest.__doc__)
#
#user_list = []
user_list = {'Bob': 1, 'Tim': 0, 'Sal': 1, 'Mal': 0, 'Ron': 0}
user = 'Bob'

def check_auth(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if user_list.get(user) and user_list.get(user) not in user_list:
            result = func(*args, **kwargs)
            return result
        else:
            print(f'{user} is not an admin to add users or already in a user_list')
    return wrapper

@check_auth
def add_user(user_name):
    new_dict = {user_name: 0}
    user_list.update(new_dict)
    return user_list



add_user('Fill')
add_user('Tim')
add_user('Tim')
add_user('Bim')
print(user_list)