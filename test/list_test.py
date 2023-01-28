# my_list = [1, 2, 4, 5, 6]
# new_element = 3
#
# # Find the right place to insert new_element
# for i in range(len(my_list)):
#     print(i)
#     if new_element < my_list[i]:
#         print("find i: " +str(i))
#         my_list.insert(i, new_element)
#         start_index = i
#         for j in range(start_index,len(my_list)):
#             my_list[j] += 1
#         break
# else:
#     my_list.append(new_element)

numbers = [1, 2, 3, 4, 5]
current = numbers[0]
for i in range(1, len(numbers)):
    print(current, "->", end=" ")
    current = numbers[i]
print(current)

