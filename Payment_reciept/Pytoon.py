def calculate_total_cost(base_price, discount_rate):
    discount_amount = base_price * (discount_rate / 100)
    final_total = base_price - discount_amount
    return final_total


def get_valid_payment(total_due):
    while True:
        user_input = input("Enter amount paid (RM): ").strip()

        is_numeric = True
        dots = 0
        for ch in user_input:
            if ch == ".":
                dots = dots + 1
            elif ch < "0" or ch > "9":
                is_numeric = False
                break

        if is_numeric == False or dots > 1 or user_input == "" or user_input == ".":
            print("Error: Invalid input. Please enter a valid numerical value.")
            continue

        amount_paid = float(user_input)

        if amount_paid < total_due:
            print(f"Error: Insufficient amount! You still owe RM {total_due - amount_paid:.2f}")
        else:
            change = amount_paid - total_due
            return amount_paid, change


def generate_receipt(booking_id, cust_name, service, base_price, discount_rate, total_due, amount_paid, change):

    print("\n" + "=" * 42)
    print("SHINE ON WHEELS RECEIPT")
    print("=" * 42)
    print(f"Booking ID   : {booking_id}")
    print(f"Customer Name: {cust_name}")
    print(f"Service Type : {service}")
    print(f"Base Price   : RM {base_price:.2f}")
    print(f"Discount     : {discount_rate:.1f}%")
    print("-" * 42)
    print(f"Total Due    : RM {total_due:.2f}")
    print(f"Amount Paid  : RM {amount_paid:.2f}")
    print(f"Change Given : RM {change:.2f}")
    print(f"Status       : PAID")
    print("=" * 42 + "\n")


def save_payment_record(payment_id, booking_id, total, paid, change, filename="payments.txt"):
    try:
        with open(filename, "a") as f:
            record = f"{payment_id},{booking_id},{total:.2f},{paid:.2f},{change:.2f},PAID\n"
            f.write(record)
        print("Payment record successfully saved.")
    except Exception as e:
        print(f"File handling error: {e}")


def process_payment_flow(booking_data):
    b_id = booking_data[0]
    name = booking_data[1]
    srv = booking_data[2]
    price = float(booking_data[3])
    discount = float(booking_data[4])

    #calculate amount
    total_due = calculate_total_cost(price, discount)
    print(f"\nFinal Calculated Total: RM {total_due:.2f}")

    #receive and verify payment
    paid, change = get_valid_payment(total_due)

    #print receipt on the screen
    generate_receipt(b_id, name, srv, price, discount, total_due, paid, change)

    #write to file. Integrated with the phone's system!
    pay_id = "PAY" + b_id.replace("BK", "")
    save_payment_record(pay_id, b_id, total_due, paid, change)

    return True

  #this just for testing!
if __name__ == "__main__":
    sample_booking = ["BK1001", "Aziz", "Full Detailing", 150.0, 10.0]
    process_payment_flow(sample_booking)
