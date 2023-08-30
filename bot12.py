from collections import UserDict
from datetime import datetime
import pickle

ADDRESSBOOK = {}

def input_error(wrap):
    def inner(*args):
        try:
            return wrap(*args)
        except IndexError:
            return "Please, give me name and phone"
        except KeyError:
            return "Contact not found. Please enter a valid name."
        except ValueError:
            return "Invalid input. Please enter a valid name and phone number."
        except TypeError as e:
            if "add_handler()" in str(e):
                return "Missing name and phone. Please provide both."
            raise e
    return inner

@input_error
def add_handler(name, phone):
    name = name.title()
    ADDRESSBOOK[name] = phone
    return f"Contact {name} with phone {phone} saved"


def exit_handler(*args):
    return "Good bye"

def enter_handler(*args):
    return "How can I help you?"

@input_error
def change_phone(name, phone):
    ADDRESSBOOK[name.title()] = phone
    return f"Phone number for contact {name} has been updated to {phone}."

@input_error
def get_phone(name):
    return f"The phone number for contact {name} is {ADDRESSBOOK[name.title()]}."

def show_all_contacts():
    if not ADDRESSBOOK:
        return "No contacts found."

    result = "Addressbook:\n"
    for name, phone in ADDRESSBOOK.items():
        result += f"{name}: {phone}\n"
    return result

def command_parser(raw_str: str):
    elements = raw_str.split()
    for func, keys in COMMANDS.items():
        if elements[0].lower() in keys:
            return func, elements[1:]

    return None, []

COMMANDS = {
    add_handler: ["add"],
    exit_handler: ["good bye", "close", "exit"],
    enter_handler: ["hello"],
    change_phone: ["change"],
    show_all_contacts: ["show", "show all", "show all contacts"],
    get_phone: ["get", "get phone"]
}


def main():
    while True:
        user_input = input(">>> ")
        if not user_input:
            continue
        func, data = command_parser(user_input)

        if func:
            if func == show_all_contacts:
                result = func()
            else:
                result = func(*data)
            print(result)
            if func == exit_handler:
                break
        else:
            print("Invalid command. Please try again.")

class Field:
    def __init__(self, value=None):
        self.value = value

    def edit(self, new_value):
        self.value = new_value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__()
        self.value = self.validate_phone(value)

    def validate_phone(self, value):
        return value

class Birthday(Field):
    def __init__(self, value):
        super().__init__()
        self.value = self.validate_birthday(value)

    def validate_birthday(self, value):
        return value


class Record:
    def __init__(self, name: Name, phone: Phone=None, birthday: Birthday = None):
        self.name = name
        self.phones = []
        self.birthday = birthday

    def add_phone(self, phone):
        self.phones.append(phone)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.edit(new_phone)
                break

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now()
            next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day)
            if today > next_birthday:
                next_birthday = next_birthday.replace(year=today.year + 1)
            days_left = (next_birthday - today).days
            return days_left
        else:
            return None


class AddressBook(UserDict):
    def dump(self):
        with open(self.file, 'wb') as file:
            pickle.dump((self.data, self.last_record_id, self.records), file)


    def load(self):
        if not self.file.exists():
            return
        with open(self.file, 'rb') as file:
            self.last_record_id, self.records = pickle.load(file)

    def search(self, search_str):
        result = []
        for name, record in self.data.items():
            if search_str.lower() in name.lower():
                result.append(record)
            for phone in record.phones:
                if search_str in phone.value:
                    result.append(record)
                for field in record.fields:
                    if search_str in field.value:
                        result.append(record)
        return result

    def add_record(self, record):
        self.data[record.name.value] = record

    def __getitem__(self, name):
        return self.data[name]

    def find_records_by_name(self, name):
        return [record for record in self.data.values() if record.name.value == name]

    def find_records_by_phone(self, phone):
        return [record for record in self.data.values() if any(p.value == phone for p in record.phones)]


if __name__ == "__main__":
    main()