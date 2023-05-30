import re


class TextModifier:
    def __init__(self):
        pass

    @staticmethod
    def extract_english_words_from_text(file_path):
        """
        Extracts English words from a text file.

        Args:
            file_path (str): The path of the text file to be processed.

        Returns:
            List[str]: A list of English words found in the text file.

        """
        english_words = []

        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
            words = re.findall(r"[A-Za-z]+(?: [A-Za-z0-9.]+)*", text)

            for word in words:
                if len(word) > 1:
                    english_words.append(word)

        problem_list = list(set(english_words))
        return problem_list

    @staticmethod
    def modify_text_file_by_word_list(file_path, problem_list, replacement_list):
        """
        Modifies a text file by replacing specified words with corresponding replacements.

        Args:
            file_path (str): The path of the text file to be modified.
            problem_list (List[str]): A list of words to be replaced.
            replacement_list (List[str]): A list of replacement words corresponding to the problem list.
        
        Returns:
            None. Changes are made directly. 

        """
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        modified_lines = []
        for line in lines:
            for i in range(len(problem_list)):
                line = line.replace(problem_list[i], replacement_list[i])
            modified_lines.append(line)

        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(modified_lines)
