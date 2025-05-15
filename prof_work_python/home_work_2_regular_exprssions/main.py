from pprint import pprint
import csv
import re


def fix_name_fields(contact):
    full_name = " ".join(contact[:3]).strip()
    parts = full_name.split()
    if len(parts) == 2:
        contact[0], contact[1] = parts[0], parts[1]
        contact[2] = ""
    elif len(parts) == 3:
        contact[0], contact[1], contact[2] = parts
    return contact


def fix_phone_number(phone):
    phone = phone.strip()
    pattern = r'(?:\+7|8)[\s$-]*(\d{3})[\s$-]*(\d{3})[\s$-]*(\d{2})[\s$-]*(\d{2})(?:\s+(доб\.|доб)\.?[\s\-]*(\d+))?'
    match = re.match(pattern, phone)

    if not match:
        return phone

    g1, g2, g3, g4 = match.group(1), match.group(2), match.group(3), match.group(4)
    add = match.group(6)

    base = f"+7({g1}){g2}-{g3}-{g4}"
    if add:
        base += f" доб.{add}"

    return base


def merge_duplicates(contacts):
    merged = {}
    for contact in contacts:
        key = (contact[0], contact[1])
        if key not in merged:
            merged[key] = contact
        else:
            existing = merged[key]
            for i in range(len(contact)):
                if contact[i]:
                    existing[i] = contact[i]
    return list(merged.values())


# Чтение CSV
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)

# Исправление полей ФИО
fixed_contacts = []
for contact in contacts_list:
    fixed_contact = fix_name_fields(contact.copy())
    fixed_contacts.append(fixed_contact)

# Исправление телефонов
for contact in fixed_contacts:
    contact[5] = fix_phone_number(contact[5])

# Объединение дубликатов
final_contacts = merge_duplicates(fixed_contacts)

# Сохранение результата
with open("phonebook.csv", "w", encoding="utf-8", newline='') as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(final_contacts)

# Для проверки — вывод
pprint(final_contacts)