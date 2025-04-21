import streamlit as st
import sqlite3

class AirlineSeating:
    def __init__(self, rows=10, seat_labels="ABCDEF"):
        self.rows = rows
        self.seat_labels = seat_labels
        self.db_connection = sqlite3.connect("seats.db")  
        self.create_table()  
        self.seats = {}
        self.create_seats()

    def create_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS seats
                        (seat TEXT PRIMARY KEY, status TEXT)''')
        self.db_connection.commit()

    def create_seats(self):
        cursor = self.db_connection.cursor()
        for row in range(1, self.rows + 1):
            for letter in self.seat_labels:
                seat = f"{row}{letter}"
                cursor.execute("INSERT OR IGNORE INTO seats (seat, status) VALUES (?, ?)", (seat, "Available"))
        self.db_connection.commit()

    def get_seat_status(self, seat):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT status FROM seats WHERE seat = ?", (seat,))
        result = cursor.fetchone()
        return result[0] if result else None

    def update_seat_status(self, seat, status):
        cursor = self.db_connection.cursor()
        cursor.execute("UPDATE seats SET status = ? WHERE seat = ?", (status, seat))
        self.db_connection.commit()

    def book_seat(self, seat):
        status = self.get_seat_status(seat)
        if status == "Available":
            self.update_seat_status(seat, "Booked")
            return True, f"Seat {seat} booked successfully!"
        elif status == "Booked":
            return False, f"Seat {seat} is already booked!"
        else:
            return False, f"Invalid seat number: {seat}"

    def cancel_seat(self, seat):
        status = self.get_seat_status(seat)
        if status == "Booked":
            self.update_seat_status(seat, "Available")
            return True, f"Seat {seat} canceled successfully."
        elif status == "Available":
            return False, f"Seat {seat} is not currently booked."
        else:
            return False, f"Invalid seat number: {seat}"

    def auto_assign_best_seat(self):
        for row in range(1, self.rows + 1):
            for letter in self.seat_labels:
                seat = f"{row}{letter}"
                if self.get_seat_status(seat) == "Available":
                    self.update_seat_status(seat, "Booked")
                    return seat, f"Best available seat {seat} has been booked!"
        return None, "No seats available."

    def get_seating_display(self):
        layout = []
        for row in range(1, self.rows + 1):
            row_display = []
            for idx, letter in enumerate(self.seat_labels):
                seat = f"{row}{letter}"
                status = self.get_seat_status(seat)
                color = "#28a745" if status == "Available" else "#dc3545"
                row_display.append((seat, color))
                if idx == 2:
                    row_display.append(("AISLE", None))
            layout.append(row_display)
            if row == 5:
                layout.append([("ROW GAP", None)])
        return layout


st.set_page_config(page_title="Airline Seat Booking", layout="centered")
st.title("✈️ SkySeats: Smart Airline Seat Allocation ")

if 'airline' not in st.session_state:
    st.session_state.airline = AirlineSeating()

airline = st.session_state.airline

st.subheader("Manage Your Seat")
action = st.radio("Choose action:", ["Book a seat", "Cancel a seat"])
seat_input = st.text_input("Enter seat number (e.g., 1A)").upper()

if st.button("Submit"):
    if seat_input:
        if action == "Book a seat":
            success, msg = airline.book_seat(seat_input)
        else:
            success, msg = airline.cancel_seat(seat_input)

        if success:
            st.success(msg)
        else:
            st.warning(msg)
    else:
        st.error("Please enter a valid seat number.")

if st.button("Auto-Assign Seat"):
    seat, msg = airline.auto_assign_best_seat()
    if seat:
        st.success(msg)
    else:
        st.warning(msg)

st.subheader("Seating Layout")
seating = airline.get_seating_display()

for row in seating:
    if row == [("ROW GAP", None)]:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        continue

    cols = st.columns(len(row))
    for i, (seat_label, color) in enumerate(row):
        if seat_label == "AISLE":
            cols[i].markdown("<div style='width: 20px;'></div>", unsafe_allow_html=True)
        else:
            cols[i].markdown(
                f"""
                <div style='
                    background-color:{color};
                    text-align:center;
                    color:white;
                    width: 80px;
                    height: 50px;
                    line-height: 50px;
                    border-radius:10px;
                    font-weight:bold;
                    font-size:16px;
                    margin: 4px auto;
                '>{seat_label}</div>
                """, unsafe_allow_html=True
            )
