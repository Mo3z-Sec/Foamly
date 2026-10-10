# Data & File Management (1.7) - Shine On Wheels
# Other modules (booking, payment) import these functions instead of
# reading/writing the booking file themselves.
from datetime import datetime

BOOKING_FILE = "booking_records.txt"
CUSTOMER_FILE = "customer_records.txt"
PAYMENT_FILE = "payments.txt"

SEPARATOR = " | "
BOOKING_FIELDS = [
    "booking_id", "customer_id", "customer_name", "car_type", "service",
    "price", "discount", "date", "time", "location", "status",
]
VALID_STATUSES = ["Confirmed", "Cancelled", "Completed"]


# ---------------------------------------------------------------
# Setup and error handling (1.7.4)
# ---------------------------------------------------------------
def ensure_data_files():
    """Create any missing data file so the program never crashes on a first run."""
    for filename in [BOOKING_FILE, CUSTOMER_FILE, PAYMENT_FILE]:
        try:
            with open(filename, "a"):
                pass
        except OSError as e:
            print(f"File error: cannot access {filename} ({e})")


def clean_text(text):
    """Remove characters that would break the ' | ' file format."""
    return str(text).replace("|", "-").replace("\n", " ").strip()


def validate_booking(booking):
    """Return (True, '') if the booking is valid, otherwise (False, reason)."""
    for field in BOOKING_FIELDS:
        if field not in booking or str(booking[field]).strip() == "":
            return False, f"Missing value for '{field}'."

    try:
        if float(booking["price"]) < 0:
            return False, "Price cannot be negative."
        discount = float(booking["discount"])
        if discount < 0 or discount > 100:
            return False, "Discount must be between 0 and 100."
    except ValueError:
        return False, "Price and discount must be numbers."

    try:
        datetime.strptime(booking["date"], "%d/%m/%Y")
    except ValueError:
        return False, "Date must be in DD/MM/YYYY format."

    try:
        datetime.strptime(booking["time"], "%H:%M")
    except ValueError:
        return False, "Time must be in HH:MM format."

    if booking["status"] not in VALID_STATUSES:
        return False, "Status must be Confirmed, Cancelled or Completed."

    return True, ""


# ---------------------------------------------------------------
# Convert between a booking dictionary and one line in the file
# ---------------------------------------------------------------
def record_to_line(booking):
    return (
        f"{booking['booking_id']}{SEPARATOR}{booking['customer_id']}{SEPARATOR}"
        f"{clean_text(booking['customer_name'])}{SEPARATOR}{booking['car_type']}{SEPARATOR}"
        f"{booking['service']}{SEPARATOR}{float(booking['price']):.2f}{SEPARATOR}"
        f"{float(booking['discount']):.1f}{SEPARATOR}{booking['date']}{SEPARATOR}"
        f"{booking['time']}{SEPARATOR}{clean_text(booking['location'])}{SEPARATOR}"
        f"{booking['status']}\n"
    )


def line_to_record(line):
    """Return a booking dictionary, or None if the line is damaged."""
    parts = line.strip().split(SEPARATOR)
    if len(parts) != len(BOOKING_FIELDS):
        return None
    try:
        return {
            "booking_id": parts[0],
            "customer_id": parts[1],
            "customer_name": parts[2],
            "car_type": parts[3],
            "service": parts[4],
            "price": float(parts[5]),
            "discount": float(parts[6]),
            "date": parts[7],
            "time": parts[8],
            "location": parts[9],
            "status": parts[10],
        }
    except ValueError:
        return None


# ---------------------------------------------------------------
# Read booking records (1.7.2)
# ---------------------------------------------------------------
def read_booking_records():
    """Return a list of booking dictionaries. Damaged lines are skipped."""
    records = []
    try:
        with open(BOOKING_FILE, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        return records
    except OSError as e:
        print(f"File error: cannot read {BOOKING_FILE} ({e})")
        return records

    for number, line in enumerate(lines, 1):
        if line.strip() == "":
            continue
        record = line_to_record(line)
        if record is None:
            print(f"Warning: skipped damaged record on line {number}.")
        else:
            records.append(record)
    return records


def get_booking_record(booking_id):
    """Return one booking dictionary, or None if it does not exist."""
    for record in read_booking_records():
        if record["booking_id"] == booking_id:
            return record
    return None


def generate_booking_id():
    """Next free booking ID, e.g. BK1001, BK1002 ..."""
    highest = 1000
    for record in read_booking_records():
        number = record["booking_id"].replace("BK", "")
        if number.isdigit() and int(number) > highest:
            highest = int(number)
    return "BK" + str(highest + 1)


# ---------------------------------------------------------------
# Store booking records (1.7.1)
# ---------------------------------------------------------------
def store_booking_record(booking):
    """Add one new booking to the file. Returns True if saved."""
    valid, reason = validate_booking(booking)
    if not valid:
        print(f"Cannot save booking: {reason}")
        return False

    if get_booking_record(booking["booking_id"]) is not None:
        print("Cannot save booking: that Booking ID already exists.")
        return False

    try:
        with open(BOOKING_FILE, "a") as file:
            file.write(record_to_line(booking))
    except OSError as e:
        print(f"File error: cannot save booking ({e})")
        return False
    return True


def write_all_booking_records(records):
    """Overwrite the file with the given list. Returns True if saved."""
    try:
        with open(BOOKING_FILE, "w") as file:
            for record in records:
                file.write(record_to_line(record))
    except OSError as e:
        print(f"File error: cannot save bookings ({e})")
        return False
    return True


# ---------------------------------------------------------------
# Update booking records (1.7.3)
# ---------------------------------------------------------------
def update_booking_record(booking_id, field, new_value):
    """Change one field of one booking. Returns True if updated."""
    if field not in BOOKING_FIELDS or field == "booking_id":
        print("Cannot update: that field cannot be changed.")
        return False

    records = read_booking_records()
    for record in records:
        if record["booking_id"] == booking_id:
            old_value = record[field]
            record[field] = new_value
            valid, reason = validate_booking(record)
            if not valid:
                record[field] = old_value
                print(f"Cannot update booking: {reason}")
                return False
            if field in ("price", "discount"):
                record[field] = float(new_value)
            return write_all_booking_records(records)

    print("Cannot update: booking not found.")
    return False


# ---------------------------------------------------------------
# Input validation helpers (1.7.4) - other modules can reuse these
# ---------------------------------------------------------------
def get_valid_text(prompt):
    while True:
        text = input(prompt).strip()
        if text == "":
            print("Input cannot be empty.")
        else:
            return clean_text(text)


def get_valid_number(prompt, minimum=0, maximum=None):
    while True:
        text = input(prompt).strip()
        try:
            value = float(text)
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue
        if value < minimum or (maximum is not None and value > maximum):
            print("Number is out of range.")
            continue
        return value


def get_valid_choice(prompt, options):
    """Show a numbered list and return the chosen option."""
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    while True:
        text = input(prompt).strip()
        if text.isdigit() and 1 <= int(text) <= len(options):
            return options[int(text) - 1]
        print("Invalid choice. Please try again.")


def get_valid_date(prompt):
    while True:
        text = input(prompt).strip()
        try:
            datetime.strptime(text, "%d/%m/%Y")
            return text
        except ValueError:
            print("Invalid date. Use DD/MM/YYYY, e.g. 25/12/2026.")


def get_valid_time(prompt):
    while True:
        text = input(prompt).strip()
        try:
            datetime.strptime(text, "%H:%M")
            return text
        except ValueError:
            print("Invalid time. Use HH:MM, e.g. 14:00.")


# ---------------------------------------------------------------
# Simple menu to demonstrate and test this part
# ---------------------------------------------------------------
def show_all_records():
    records = read_booking_records()
    if len(records) == 0:
        print("No booking records found.")
        return
    print("\nBooking ID | Customer | Service | Price | Date | Time | Status")
    print("-" * 66)
    for r in records:
        print(f"{r['booking_id']:<10} | {r['customer_name']:<10} | {r['service']:<14} | "
              f"{r['price']:>6.2f} | {r['date']} | {r['time']} | {r['status']}")
    print(f"\nTotal records: {len(records)}")


def update_menu():
    print("\n--- UPDATE BOOKING RECORD ---")
    booking_id = input("Enter Booking ID: ").strip()
    if get_booking_record(booking_id) is None:
        print("Booking not found.")
        return

    editable = ["car_type", "service", "price", "discount", "date", "time", "location", "status"]
    field = get_valid_choice("Choose field to update: ", editable)

    if field == "status":
        new_value = get_valid_choice("Choose new status: ", VALID_STATUSES)
    elif field in ("price", "discount"):
        new_value = get_valid_number(f"Enter new {field}: ")
    elif field == "date":
        new_value = get_valid_date("Enter new date (DD/MM/YYYY): ")
    elif field == "time":
        new_value = get_valid_time("Enter new time (HH:MM): ")
    else:
        new_value = get_valid_text(f"Enter new {field}: ")

    if update_booking_record(booking_id, field, new_value):
        print("Booking record updated.")


def data_menu():
    ensure_data_files()
    while True:
        print("\nData & File Management")
        print("1. View all booking records")
        print("2. Update a booking record")
        print("3. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            show_all_records()
        elif choice == "2":
            update_menu()
        elif choice == "3":
            print("Program ended.")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    data_menu()