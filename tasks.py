from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    orders = get_orders()
    open_robot_order_website()
    for row in orders:
        close_annoying_modal()
        fill_the_form(row)
        pdf_path = store_receipt_as_pdf(row['Order number'])
        screenshot_path = screenshot_robot(row['Order number'])
        embed_screenshot_to_receipt(screenshot_path, pdf_path)
        order_another()
        archive_reciepts()

def get_orders():
    HTTP().download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    return Tables().read_table_from_csv("orders.csv", header=True)


def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def close_annoying_modal():
    browser.page().click("button:text('OK')")


def fill_the_form(order):
    page = browser.page()
    page.select_option("#head", order["Head"])
    page.check(f"#id-body-{order['Body']}")
    page.get_by_placeholder("Enter the part number for the legs").fill(order["Legs"])
    page.fill("#address", order["Address"])
    page.click("#preview")
    while page.locator("#order").is_visible():
        page.click("#order")


def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()
    pdf = PDF()
    path = f"output/reciepts/order-{order_number}.pdf"
    pdf.html_to_pdf(receipt, path)
    return path


def screenshot_robot(order_number):
    page = browser.page()
    path = f"output/screenshots/order-{order_number}.png"
    page.screenshot(path=path)
    return path


def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[pdf_file, screenshot],
        target_document=pdf_file
    )


def order_another():
    browser.page().click("#order-another")


def archive_reciepts():
    Archive().archive_folder_with_zip('./output/reciepts', 'output/reciepts.zip')

