# when query is ordering and the query is using a GROUP BY clause, you can only order by columns that are included in the GROUP BY clause or are used within an aggregate function.
# careful select_extend & groupby
# operator.lt
# [limit_id for dictionary in [V[limit_id] for limit_id in limit_ids] for limit_id in dictionary]
#
# BASE_DIR = Path(__file__).resolve().parent.parent
#
#
# def ping_is_alive(model, name):
#     # model(name=name, last_ping=now()).save()  ne marche pas return 0 pas input dans la db
#     model.insert(name=name, last_ping=now()).execute()  # ok


# recall the current function call
#     # Get the current local variables as a dictionary
#     args = locals()
#
#     # Remove the function name from the dictionary
#     del args['get_candles_datas']
#
#     # Call the function with the same arguments using the dictionary
#     return get_candles_datas(**args)

# plt.xlabel('Epochs')
# ...
# plt.show()
# to
# plt.xlabel('Epochs'), plt.ylabel('Loss'), ax1.legend(), ax2.legend(), plt.tight_layout(), plt.show()

# https://github.com/TA-Lib/ta-lib-python

# class Gen:
#     def __init__(self):
#         self.x = 0
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         self.x += 1
#         return self
#
# gen = Gen()
#
# for _ in gen:
#     print(gen.x)

