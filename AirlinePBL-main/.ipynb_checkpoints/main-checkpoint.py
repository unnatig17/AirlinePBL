import streamlit as st
import sqlite3
from collections import deque

class AirlineSeating:
    def __init__(self, db_path="airline.db", rows=10, seat_labels="ABCDEF"):
        self.db_path = db_path
        self.rows = rows
        self.seat_labels = seat_labels
        self.create_table()
        self.create_seats_if_not_exists()

    def connect_db(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def create_table(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS seats (
                          seat TEXT PRIMARY KEY,
                          status TEXT,
                          special_group TEXT DEFAULT NULL)''')
        conn.commit()
        conn.close()

    def create_seats_if_not_exists(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        for row in range(1, self.rows + 1):
            for letter in self.seat_labels:
                seat = f"{row}{letter}"
                cursor.execute("INSERT OR IGNORE INTO seats (seat, status) VALUES (?, ?)", (seat, "Available"))
        conn.commit()
        conn.close()

    def get_seat_status(self, seat):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM seats WHERE seat = ?", (seat,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "Invalid"

    def get_seat_group(self, seat):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT special_group FROM seats WHERE seat = ?", (seat,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] else None

    def book_seat(self, seat, group_type=None):
        if self.get_seat_status(seat) == "Available":
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE seats SET status = 'Booked', special_group = ? WHERE seat = ?", (group_type, seat))
            conn.commit()
            conn.close()
            return True, f"Seat {seat} booked successfully!"
        elif self.get_seat_status(seat) == "Invalid":
            return False, f"Invalid seat number: {seat}"
        else:
            return False, f"Seat {seat} is already booked!"

    def cancel_seat(self, seat):
        if self.get_seat_status(seat) == "Booked":
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE seats SET status = 'Available', special_group = NULL WHERE seat = ?", (seat,))
            conn.commit()
            conn.close()
            return True, f"Seat {seat} canceled successfully."
        elif self.get_seat_status(seat) == "Invalid":
            return False, f"Invalid seat number: {seat}"
        else:
            return False, f"Seat {seat} is not currently booked."

    def get_seating_display(self):
        layout = []
        for row in range(1, self.rows + 1):
            row_display = []
            for idx, letter in enumerate(self.seat_labels):
                seat = f"{row}{letter}"
                status = self.get_seat_status(seat)
                group = self.get_seat_group(seat)
                if group == "Elderly":
                    color = "#ffcc00"
                elif group == "Disabled":
                    color = "#6f42c1"
                elif group == "Infant":
                    color = "#17a2b8"
                elif group == "Silent":
                    color = "#343a40"
                else:
                    color = "#28a745" if status == "Available" else "#dc3545"
                row_display.append((seat, color, group))
                if idx == 2:
                    row_display.append(("AISLE", "#ffffff", None))
            layout.append(row_display)
            if row == 5:
                layout.append([("ROW GAP", "#ffffff", None)])
        return layout

    def seat_to_index(self, seat):
        row = int(seat[:-1])
        col = self.seat_labels.index(seat[-1])
        return row - 1, col

    def index_to_seat(self, row, col):
        return f"{row + 1}{self.seat_labels[col]}"

    def find_adjacent_seats_bfs(self, start_seat, group_size):
        row_idx, col_idx = self.seat_to_index(start_seat)
        max_col = len(self.seat_labels)
        visited = set()
        queue = deque([(row_idx, col_idx, [])])

        while queue:
            r, c, path = queue.popleft()
            seat = self.index_to_seat(r, c)

            if (r, c) in visited or c >= max_col:
                continue
            visited.add((r, c))

            if self.get_seat_status(seat) != "Available":
                continue

            path = path + [seat]
            if len(path) == group_size:
                return path

            if c + 1 < max_col:
                queue.append((r, c + 1, path))

        return []

st.set_page_config(page_title="Airline Seat Booking", layout="centered")
st.title("\u2708\ufe0f SkySeats: Smart Airline Seat Allocation ")

if 'airline' not in st.session_state:
    st.session_state.airline = AirlineSeating()

airline = st.session_state.airline

action = st.radio("Choose action:", [
    "Book a seat",
    "Cancel a seat",
    "Auto-Assign with Preferences",
    "Check seat price",
    "Find Adjacent Seats (BFS)"
])

seat_input = st.text_input("Enter seat number (e.g., 1A)").upper()
group_type = None
group_size = 1

if action in ["Auto-Assign with Preferences", "Check seat price"]:
    group_type = st.selectbox("Select passenger type:", ["None", "Elderly", "Disabled", "Infant", "Silent"])
    if group_type == "None":
        group_type = None

if action == "Find Adjacent Seats (BFS)":
    group_size = st.number_input("Enter group size:", min_value=1, max_value=6, value=2)

if st.button("Submit"):
    if action == "Find Adjacent Seats (BFS)":
        if seat_input:
            result = airline.find_adjacent_seats_bfs(seat_input, group_size)
            if result:
                st.success(f"Adjacent available seats: {', '.join(result)}")
            else:
                st.warning("No adjacent seats available for the group size.")

    elif action == "Auto-Assign with Preferences":
        seat, msg = airline.auto_assign_best_seat(group_type)
        if seat:
            st.success(msg)
            price = airline.calculate_price(group_type)
            st.markdown(f"**Total fare: ₹{price:.2f}**")
        else:
            st.warning(msg)

    elif action == "Check seat price":
        if seat_input:
            status = airline.get_seat_status(seat_input)
            if status == "Invalid":
                st.warning("Invalid seat number.")
            elif status == "Booked":
                st.warning(f"Seat {seat_input} is already booked.")
            else:
                price = airline.calculate_price(group_type)
                st.success(f"Price for seat {seat_input} ({group_type or 'General'}): ₹{price:.2f}")
        else:
            st.error("Please enter a seat number to check price.")

    elif seat_input:
        if action == "Book a seat":
            success, msg = airline.book_seat(seat_input, group_type)
            if success:
                st.success(msg)
                price = airline.calculate_price(group_type)
                st.markdown(f"**Total fare: ₹{price:.2f}**")
            else:
                st.warning(msg)
        else:
            success, msg = airline.cancel_seat(seat_input)
            if success:
                st.success(msg)
            else:
                st.warning(msg)
    else:
        st.error("Please enter a valid seat number.")

st.subheader("Seating Layout")
seating = airline.get_seating_display()

for row in seating:
    if any(seat[0] == "ROW GAP" for seat in row):
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        continue

    cols = st.columns(len(row))
    for i, (seat_label, color, group) in enumerate(row):
        if seat_label == "AISLE":
            cols[i].markdown("<div style='width: 20px;'></div>", unsafe_allow_html=True)
        else:
            label_display = f"{seat_label}"
            if group:
                label_display += f"<br><span style='font-size:10px;'>({group})</span>"
            cols[i].markdown(
                f"""
                <div style='
                    background-color:{color};
                    text-align:center;
                    color:white;
                    width: 80px;
                    height: 50px;
                    line-height: 1.2em;
                    border-radius:10px;
                    font-weight:bold;
                    font-size:14px;
                    margin: 4px auto;
                    padding-top: 5px;
                '>{label_display}</div>
                """, unsafe_allow_html=True
            )