import os  # Убедитесь, что эта строка присутствует

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

def write_combined_file(file_paths, output_path):
    files_content = []
    for file_path in file_paths:
        lines = read_file(file_path)
        files_content.append((os.path.basename(file_path), len(lines), lines))
    
    # Sort files by number of lines
    files_content.sort(key=lambda x: x[1])

    with open(output_path, 'w', encoding='utf-8') as output_file:
        for file_name, line_count, lines in files_content:
            output_file.write(f"{file_name}\n{line_count}\n")
            output_file.writelines(lines)
            output_file.write('\n')

def main():
    # List of file names
    file_names = ['1.txt', '2.txt', '3.txt']
    file_paths = [os.path.join('C:/Users/admin/Documents/Netology/(2) Открытие и чтение файла, запись в файл/', file_name) for file_name in file_names]
    output_path = 'C:/Users/admin/Documents/Netology/(2) Открытие и чтение файла, запись в файл/output.txt'
    
    write_combined_file(file_paths, output_path)

if __name__ == '__main__':
    main()