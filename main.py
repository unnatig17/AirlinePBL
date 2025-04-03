from colorama import Fore, Style, init

init(autoreset=True)

class AirlineSeating:
    def __init__(self, rows=10, cols=9, aisle_columns=[3, 7], aisle_width=2):
        self.seats = {}
        self.rows = rows
        self.cols = cols
        self.aisle_columns = aisle_columns
        self.aisle_width = aisle_width
        self.create_seats()

    def create_seats(self):
        seat_letters = "ABCDEFGHIJ"
        for row in range(1, self.rows + 1):
            for letter in seat_letters[:self.cols]:
                self.seats[f"{letter}{row}"] = "Available"

    def book_seat(self, seat):
        if seat in self.seats:
            if self.seats[seat] == "Available":
                self.seats[seat] = "Booked"
                print(Fore.GREEN + f"Seat {seat} booked successfully!" + Style.RESET_ALL)
            else:
                print(Fore.RED + f" Seat {seat} is already booked!" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + f"⚠ Invalid seat number: {seat}" + Style.RESET_ALL)

    def cancel_seat(self, seat):
        if seat in self.seats:
            if self.seats[seat] == "Booked":
                self.seats[seat] = "Available"
                print(Fore.CYAN + f"Seat {seat} has been canceled and is now available." + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + f"Seat {seat} is not booked!" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + f"Invalid seat number: {seat}" + Style.RESET_ALL)

    def display_seating(self):
        print("\nAirline Seating Arrangement:")
        seat_letters = "ABCDEFGHIJ"

        for row in range(1, self.rows + 1):
            row_display = []
            for col, letter in enumerate(seat_letters[:self.cols], start=1):
                seat = f"{letter}{row}"
                if self.seats[seat] == "Available":
                    row_display.append(Fore.GREEN + seat + Style.RESET_ALL)
                else:
                    row_display.append(Fore.RED + seat + Style.RESET_ALL)
                
                if col in self.aisle_columns:
                    row_display.append(" " * (self.aisle_width * 4))

            print("  ".join(row_display))
        print()

airline = AirlineSeating(rows=10, cols=9, aisle_columns=[3, 7], aisle_width=2)

while True:
    airline.display_seating()

    print("\nOptions:")
    print("1. Book a seat")
    print("2. Cancel a seat")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        seat = input("Enter seat number to book (e.g., A1): ").upper()
        airline.book_seat(seat)
    elif choice == "2":
        seat = input("Enter seat number to cancel (e.g., A1): ").upper()
        airline.cancel_seat(seat)
    elif choice == "3":
        print("Exiting... Have a great flight! ✈️")
        break
    else:
        print(Fore.YELLOW + "⚠ Invalid choice. Please enter 1, 2, or 3." + Style.RESET_ALL)
