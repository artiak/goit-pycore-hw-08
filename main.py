import sys
import re
import pickle
from typing import Tuple, Any, Dict, List, Callable
from book import AddressBook
from record import Record


CMD_TO_FUNC: Dict[str, str] = {}
CMD_TO_FUNC["hello"] = "_greet"
CMD_TO_FUNC["add"] = "_add_contact"
CMD_TO_FUNC["change"] = "_change_contact"
CMD_TO_FUNC["phone"] = "_show_phone"
CMD_TO_FUNC["all"] = "_show_all"
CMD_TO_FUNC["add-birthday"] = "_add_birthday"
CMD_TO_FUNC["show-birthday"] = "_show_birthday"
CMD_TO_FUNC["birthdays"] = "_birthdays"
CMD_TO_FUNC["close"] = "_exit"
CMD_TO_FUNC["exit"] = "_exit"

FILE_NAME = "addressbook.pkl"

book: AddressBook = None


def main():
    _init()
    while True:
        str_input: str = input("Enter a command: ")
        tuple_input: Tuple[str, list] = _parse_input(str_input)

        cmd: str = tuple_input[0]

        if not cmd in CMD_TO_FUNC:
            print("Invalid command\n")
            continue

        args: list = tuple_input[1]

        _call_function(cmd, args)


def _init() -> None:
    global book
    book = load_data()
    print("Welcome to the assistant bot!\n")


def _parse_input(input: str) -> Tuple[str, list]:
    list_input: List[str] = input.strip().split()

    func = list_input[0].lower()
    args = list_input[1:]

    return (func, args)


def _call_function(cmd: str, args: tuple) -> None:
    func: str = CMD_TO_FUNC[cmd]
    globs: Dict[str, Any] = globals()

    if not _is_function(func, globs):
        print(f"Function '{func}' not found\n")

        return

    globs[func](*args)


def _is_function(name: str, globs: Dict[str, Any]) -> bool:
    return name in globs and callable(globs[name])


def _input_error(func: Callable) -> Callable:
    def inner(*args):
        try:
            func(*args)
        except KeyError:
            print("Contact not foud\n")
        except ValueError:
            print("Phone number should have 10 digits\n")
        except Exception as exc:
            print(exc)
            print("")

    return inner


@_input_error
def _greet() -> None:
    print("How can I help you?\n")


@_input_error
def _add_contact(name: str, phone: str) -> None:
    if not _is_phone(phone):
        raise ValueError

    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)

    print("Contact added\n")


def _is_phone(input: str) -> bool:
    """
    Defines if input corresponds to 10 digit formats, e.g.:
        (XXX)-XXX-XXXX
         XXX-XXX-XXXX
        (XXX)XXXXXXX
         XXXXXXXXXX
    """
    pattern = r"\b\(?\d{3}\)?-?\d{3}-?\d{4}\b"

    return bool(re.match(pattern, input))


@_input_error
def _change_contact(name: str, orig_phone_num: str, upd_phone_num) -> None:
    if not name in book:
        raise KeyError

    if not _is_phone(upd_phone_num):
        raise ValueError

    record: Record = book.find(name)
    record.edit_phone(orig_phone_num, upd_phone_num)

    print("Contact updated\n")


@_input_error
def _show_phone(name: str) -> None:
    if not name in book:
        raise KeyError

    record: Record = book.find(name)

    print(record.get_phones())
    print()


def _show_all() -> None:
    for record in book.values():
        print(record)

    print()


@_input_error
def _add_birthday(name: str, birth_date: str):
    record: Record = book.find(name)
    record.add_birthday(birth_date)

    print("Birthday added\n")


@_input_error
def _show_birthday(name: str):
    record: Record = book.find(name)

    print(record.get_birthday())
    print()


@_input_error
def _birthdays():
    for birthday in book.get_upcoming_birthdays():
        print(birthday)
    print("\n")


def _exit() -> None:
    save_data(book)
    print("Good bye\n")

    sys.exit(0)


def load_data() -> AddressBook:
    try:
        with open(FILE_NAME, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def save_data(book):
    with open(FILE_NAME, "wb") as f:
        pickle.dump(book, f)


# TESTING


def _should_save_and_load():
    name = "Art"
    orig_record = Record(name)
    phone_num = "1111111111"
    orig_record.add_phone(phone_num)
    str_bday = "03.08.1987"
    orig_record.add_birthday(str_bday)
    orig_book = AddressBook()
    orig_book.add_record(orig_record)
    save_data(orig_book)
    loaded_book = load_data()
    loaded_record: Record = list(loaded_book.data.values())[0]
    assert name == loaded_record.get_name().get_value()
    assert phone_num == loaded_record.get_phones()[0].get_value()
    loaded_bday = loaded_record.get_birthday().get_value()
    assert str_bday == AddressBook._to_str(loaded_bday)

# uncomment for testing
# if __name__ == "__main__":
    # _should_save_and_load()

main()
