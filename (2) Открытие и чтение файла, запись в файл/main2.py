def read_recipes(file_path):
    cook_book = {}
    with open(file_path, encoding='utf-8') as file:
        while True:
            dish_name = file.readline().strip()
            if not dish_name:
                break
            ingredients_count = int(file.readline().strip())
            ingredients = []
            for _ in range(ingredients_count):
                ingredient_name, quantity, measure = file.readline().strip().split(' | ')
                ingredients.append({
                    'ingredient_name': ingredient_name,
                    'quantity': int(quantity),
                    'measure': measure
                })
            cook_book[dish_name] = ingredients
            file.readline()  # пропускаем пустую строку
    return cook_book

def get_shop_list_by_dishes(dishes, person_count, cook_book):
    shop_list = {}
    for dish in dishes:
        if dish in cook_book:
            for ingredient in cook_book[dish]:
                name = ingredient['ingredient_name']
                if name not in shop_list:
                    shop_list[name] = {
                        'measure': ingredient['measure'],
                        'quantity': ingredient['quantity'] * person_count
                    }
                else:
                    shop_list[name]['quantity'] += ingredient['quantity'] * person_count
    return shop_list

def main():
    file_path = 'C:/Users/admin/Documents/Netology/(2) Открытие и чтение файла, запись в файл/recipes.txt'  # Замените на ваш путь к файлу рецептов
    cook_book = read_recipes(file_path)
    dishes = ['Запеченный картофель', 'Омлет']
    person_count = 2
    shopping_list = get_shop_list_by_dishes(dishes, person_count, cook_book)
    for ingredient, details in shopping_list.items():
        print(f"{ingredient}: {details}")

if __name__ == "__main__":
    main()