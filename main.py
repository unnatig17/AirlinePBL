import streamlit as st
import json
import os

SEAT_DATA_FILE = "seat_data.json"

def initialize_seats():
    return {f"{r}{c}": "available" for r in range(1, 31) for c in "ABCDEF"}

if os.path.exists(SEAT_DATA_FILE):
    with open(SEAT_DATA_FILE, "r") as f:
        seats = json.load(f)
else:
    seats = initialize_seats()

def save_seats():
    with open(SEAT_DATA_FILE, "w") as f:
        json.dump(seats, f)

st.title("Airline Seat Booking System")
st.subheader("Seat Layout")

for row in range(1, 31):
    cols = st.columns(7, gap="small")
    for i, col in enumerate("ABCDEF"):
        if i == 3:
            cols[i].write(" ")
        seat_key = f"{row}{col}"
        color = "red" if seats[seat_key] == "booked" else "green"
        button_style = f"background-color: {color}; color: white; border-radius: 5px; padding: 5px; border: none; width: 100%; text-align: center;"
        cols[i if i < 3 else i + 1].markdown(f'<button style="{button_style}">{seat_key}</button>', unsafe_allow_html=True)

st.subheader("Check or Book a Seat")
seat_input = st.text_input("Enter Seat Number (e.g., 9A)").upper()

if st.button("Check Availability"):
    if seat_input in seats:
        st.write(f"Seat {seat_input} is {seats[seat_input].capitalize()}")
    else:
        st.write("Invalid seat number.")

if st.button("Book Seat"):
    if seat_input in seats and seats[seat_input] == "available":
        seats[seat_input] = "booked"
        save_seats()
        st.write(f"Seat {seat_input} booked successfully!")
    elif seat_input in seats:
        st.write(f"Seat {seat_input} is already booked.")
    else:
        st.write("Invalid seat number.")

if st.button("Cancel Booking"):
    if seat_input in seats and seats[seat_input] == "booked":
        seats[seat_input] = "available"
        save_seats()
        st.write(f"Booking for seat {seat_input} cancelled.")
    elif seat_input in seats:
        st.write(f"Seat {seat_input} is not booked.")
    else:
        st.write("Invalid seat number.")
