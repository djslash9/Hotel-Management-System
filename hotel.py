import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hotel Management System", layout="wide")

st.title("🏨 Hotel Management System App")
menu = st.sidebar.selectbox("📂 Select Module", [
    "Overview",
    "Reception & Room Management",
    "Inventory & Kitchen Management",
    "Room Orders",
    "Staff Management",
    "Visitor & Occupancy Analytics",
    "Make a Bill",
    "Admin Panel",
    "Conclusion"
])

# --- Sample Data Storage (in-memory for demo) ---
if 'bookings' not in st.session_state:
    st.session_state.bookings = []

if 'inventory' not in st.session_state:
    st.session_state.inventory = []

if 'staff' not in st.session_state:
    st.session_state.staff = []

# --- Pages ---
def show_overview():
    st.subheader("📋 Overview of Modules")
    st.markdown("""
    - Reception & Room Management  
    - Inventory & Kitchen Management  
    - Staff Management  
    - Visitor & Occupancy Analytics  
    - Admin & Financial Dashboard  
    """)

def reception_room_management():
    st.subheader("🛏️ Reception & Room Management")

    sub_tab = st.radio("Select Action", ["Book Room", "Check In/Out", "View Bookings"])
    
    if sub_tab == "Book Room":
        with st.form("booking_form"):
            name = st.text_input("Customer Name")
            room = st.number_input("Room Number", 1, 100, 1)
            checkin = st.date_input("Check-In Date")
            checkout = st.date_input("Check-Out Date")
            submitted = st.form_submit_button("Book")
            if submitted:
                st.session_state.bookings.append({
                    "Name": name,
                    "Room": room,
                    "Check-In": checkin,
                    "Check-Out": checkout,
                    "Status": "Booked"
                })
                st.success("Booking successful.")

    elif sub_tab == "Check In/Out":
        if st.session_state.bookings:
            bookings_df = pd.DataFrame(st.session_state.bookings)
            customer_list = bookings_df["Name"] + " (Room " + bookings_df["Room"].astype(str) + ")"
            selected = st.selectbox("Select Customer", customer_list)
            action = st.radio("Action", ["Check In", "Check Out"])
            if st.button("Update Status"):
                for booking in st.session_state.bookings:
                    if f"{booking['Name']} (Room {booking['Room']})" == selected:
                        booking["Status"] = "Checked In" if action == "Check In" else "Checked Out"
                        st.success(f"{booking['Name']} has been {booking['Status']}")

    else:
        if st.session_state.bookings:
            st.dataframe(pd.DataFrame(st.session_state.bookings))
        else:
            st.info("No bookings yet.")

def room_orders():
    st.subheader("🧾 Room Orders")
    
    if not st.session_state.bookings:
        st.warning("No room bookings available. Add a booking first.")
        return

    # Room selection
    bookings_df = pd.DataFrame(st.session_state.bookings)
    customer_list = bookings_df["Name"] + " (Room " + bookings_df["Room"].astype(str) + ")"
    selected = st.selectbox("Select Room Booking", customer_list)

    order_type = st.radio("Order Type", ["Food", "Beverages", "Services"])

    items = {
        "Food": ["Rice & Curry", "Pasta", "Burger", "Pizza", "Salad"],
        "Beverages": ["Tea", "Coffee", "Juice", "Soda", "Water"],
        "Services": ["Room Cleaning", "Laundry", "Wake-up Call", "Spa", "Taxi Service"]
    }

    item_selected = st.multiselect("Select Items", items[order_type])
    remarks = st.text_area("Additional Notes (optional)")

    if 'orders' not in st.session_state:
        st.session_state.orders = []

    if st.button("Add Order"):
        st.session_state.orders.append({
            "Customer": selected,
            "Type": order_type,
            "Items": item_selected,
            "Remarks": remarks
        })
        st.success("Order added successfully!")

    if st.checkbox("Show All Orders"):
        if st.session_state.orders:
            st.dataframe(pd.DataFrame(st.session_state.orders))
        else:
            st.info("No orders placed yet.")



def inventory_kitchen():
    st.subheader("🍽️ Inventory & Kitchen Management")

    tabs = st.radio("Select Action", ["Stock Update", "Kitchen Out (Usage)", "Fulfill Customer Request"])

    # Initialize inventory if not present
    if 'inventory' not in st.session_state:
        st.session_state.inventory = []

    if tabs == "Stock Update":
        st.subheader("📦 Add or Update Stock")
        with st.form("update_stock"):
            item = st.text_input("Item Name")
            quantity = st.number_input("Quantity", min_value=1)
            submit = st.form_submit_button("Add / Update Stock")
            if submit:
                updated = False
                for stock in st.session_state.inventory:
                    if stock["Item"].lower() == item.lower():
                        stock["Quantity"] += quantity
                        updated = True
                        break
                if not updated:
                    st.session_state.inventory.append({"Item": item, "Quantity": quantity})
                st.success(f"Stock updated for item: {item}")

        if st.session_state.inventory:
            st.write("📋 Current Stock:")
            st.dataframe(pd.DataFrame(st.session_state.inventory))

    elif tabs == "Kitchen Out (Usage)":
        st.subheader("👨‍🍳 Kitchen Usage")
        if not st.session_state.inventory:
            st.warning("No stock available.")
            return

        items = [stock["Item"] for stock in st.session_state.inventory]
        selected_items = st.multiselect("Select Used Items", items)
        used_quantities = {}

        for item in selected_items:
            qty = st.number_input(f"Used quantity for {item}", min_value=1, key=f"used_{item}")
            used_quantities[item] = qty

        if st.button("Confirm Usage"):
            for item, qty in used_quantities.items():
                for stock in st.session_state.inventory:
                    if stock["Item"] == item:
                        stock["Quantity"] -= qty
                        if stock["Quantity"] < 0:
                            stock["Quantity"] = 0
            st.success("Kitchen usage updated.")

        if st.session_state.inventory:
            st.write("📋 Updated Stock:")
            st.dataframe(pd.DataFrame(st.session_state.inventory))

    elif tabs == "Fulfill Customer Request":
        st.subheader("🧾 Fulfill Customer Request from Stock")

        if 'bookings' not in st.session_state or not st.session_state.bookings:
            st.warning("No customer bookings.")
            return

        if not st.session_state.inventory:
            st.warning("Stock is empty.")
            return

        bookings_df = pd.DataFrame(st.session_state.bookings)
        customer_list = bookings_df["Name"] + " (Room " + bookings_df["Room"].astype(str) + ")"
        selected_customer = st.selectbox("Select Customer", customer_list)

        stock_items = [stock["Item"] for stock in st.session_state.inventory]
        selected_items = st.multiselect("Items to send to Kitchen", stock_items)
        kitchen_qty = {}

        for item in selected_items:
            qty = st.number_input(f"Quantity for {item}", min_value=1, key=f"cust_{item}")
            kitchen_qty[item] = qty

        if st.button("Send to Kitchen"):
            for item, qty in kitchen_qty.items():
                for stock in st.session_state.inventory:
                    if stock["Item"] == item:
                        stock["Quantity"] -= qty
                        if stock["Quantity"] < 0:
                            stock["Quantity"] = 0
            if 'orders' not in st.session_state:
                st.session_state.orders = []
            st.session_state.orders.append({
                "Customer": selected_customer,
                "Type": "Kitchen Request",
                "Items": list(kitchen_qty.keys()),
                "Remarks": "Customer order fulfilled from stock"
            })
            st.success(f"Order for {selected_customer} sent to kitchen.")

        if st.session_state.inventory:
            st.write("📋 Remaining Stock:")
            st.dataframe(pd.DataFrame(st.session_state.inventory))


def staff_management():
    st.subheader("👥 Staff Management")

    action = st.radio("Select", ["Add Staff", "View Staff", "Assign Shift"])

    if action == "Add Staff":
        with st.form("add_staff"):
            name = st.text_input("Staff Name")
            role = st.selectbox("Role", ["Receptionist", "Chef", "Housekeeping", "Manager"])
            submitted = st.form_submit_button("Add Staff")
            if submitted:
                st.session_state.staff.append({"Name": name, "Role": role})
                st.success("Staff added.")

    elif action == "View Staff":
        if st.session_state.staff:
            st.dataframe(pd.DataFrame(st.session_state.staff))
        else:
            st.info("No staff added yet.")

    elif action == "Assign Shift":
        if st.session_state.staff:
            staff_df = pd.DataFrame(st.session_state.staff)
            name = st.selectbox("Select Staff", staff_df["Name"])
            shift = st.selectbox("Shift", ["Morning", "Evening", "Night"])
            st.success(f"{name} assigned to {shift} shift (for demo only).")
        else:
            st.warning("Add staff first.")

def visitor_analytics():
    st.subheader("📊 Visitor & Occupancy Analytics")
    if st.session_state.bookings:
        df = pd.DataFrame(st.session_state.bookings)
        st.metric("Total Bookings", len(df))
        st.metric("Currently Checked In", len(df[df["Status"] == "Checked In"]))
        st.bar_chart(df["Status"].value_counts())
    else:
        st.info("No visitor data available.")
        
def make_a_bill():
    st.subheader("🧾 Make a Bill")

    if not st.session_state.bookings:
        st.warning("No bookings available.")
        return

    bookings_df = pd.DataFrame(st.session_state.bookings)
    customer_list = bookings_df["Name"] + " (Room " + bookings_df["Room"].astype(str) + ")"
    selected = st.selectbox("Select Customer Booking", customer_list)

    selected_booking = None
    for b in st.session_state.bookings:
        if f"{b['Name']} (Room {b['Room']})" == selected:
            selected_booking = b
            break

    room_charge = 5000  # Example room charge per stay
    st.write("🏠 **Room Charge:** Rs.", room_charge)

    # Get orders for selected customer
    if 'orders' not in st.session_state:
        st.session_state.orders = []

    order_items = [o for o in st.session_state.orders if o["Customer"] == selected]

    food_price = {
        "Rice & Curry": 700, "Pasta": 800, "Burger": 600, "Pizza": 1000, "Salad": 500,
        "Tea": 100, "Coffee": 150, "Juice": 200, "Soda": 120, "Water": 80,
        "Room Cleaning": 300, "Laundry": 400, "Wake-up Call": 150, "Spa": 1500, "Taxi Service": 1000
    }

    item_details = []
    total = room_charge

    for order in order_items:
        for item in order["Items"]:
            price = food_price.get(item, 0)
            total += price
            item_details.append({
                "Type": order["Type"],
                "Item": item,
                "Price (Rs)": price
            })

    # Display order items
    if item_details:
        st.write("🧾 **Order Details:**")
        st.dataframe(pd.DataFrame(item_details))
    else:
        st.info("No additional orders for this customer.")

    st.write("💰 **Total Bill:** Rs.", total)

    # Optional: Download as CSV
    if st.button("Download Bill"):
        bill_df = pd.DataFrame([{
            "Customer": selected_booking["Name"],
            "Room": selected_booking["Room"],
            "Check-In": selected_booking["Check-In"],
            "Check-Out": selected_booking["Check-Out"],
            "Total (Rs)": total
        }])
        bill_csv = bill_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Bill as CSV",
            data=bill_csv,
            file_name=f"bill_{selected_booking['Name']}_room{selected_booking['Room']}.csv",
            mime="text/csv"
        )


def admin_panel():
    st.subheader("🔐 Admin Panel")
    st.markdown("""
    - Staff Oversight  
    - System Configurations  
    - Financial Overview (future integration)  
    """)
    st.write("Admin Panel Coming Soon...")

def conclusion():
    st.subheader("✅ Summary")
    st.markdown("""
    - Complete hotel operation modules  
    - Real-time room and staff management  
    - Customizable for larger deployments  
    """)
    st.success("Thank you! Please reach out for full deployment.")

# --- Page Loader ---
if menu == "Overview":
    show_overview()
elif menu == "Reception & Room Management":
    reception_room_management()
elif menu == "Inventory & Kitchen Management":
    inventory_kitchen()
elif menu == "Room Orders":
    room_orders()
elif menu == "Staff Management":
    staff_management()
elif menu == "Visitor & Occupancy Analytics":
    visitor_analytics()
elif menu == "Make a Bill":
    make_a_bill()
elif menu == "Admin Panel":
    admin_panel()
elif menu == "Conclusion":
    conclusion()
