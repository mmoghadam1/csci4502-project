from pymongo import MongoClient
import zipfile
from io import BytesIO
import sys
import os


class LoanDataLoader(object):
    ORIG_MAPPINGS = [
        "credit_score",
        "first_payment_date",
        "first_time_homebuyer_flag",
        "maturity_date",
        "metro_stat_area",
        "morg_insur_percent",
        "num_units",
        "occupancy_stat",
        "combined_loan_to_val",
        "orig_debt_to_income",
        "orig_upb",
        "orig_loan_to_val",
        "orig_interest_rate",
        "channel",
        "prepay_penalty_flag",
        "product_type",
        "property_state",
        "property_type",
        "postal_code",
        "loan_seq_num",
        "loan_purpose",
        "orig_loan_term",
        "num_borrowers",
        "seller_name",
        "service_name",
        "super_conform_flag",
    ]

    MONTHLY_MAPPINGS = [
        "loan_seq_num",
        "monthly_report_period",
        "curr_actual_upb",
        "curr_loan_deliq_status",
        "loan_age",
        "remaining_months_maturity",
        "repurchase_flag",
        "modify_flag",
        "zero_bal_code",
        "zero_bal_date",
        "curr_interest_rate",
        "curr_deferred_upb",
        "due_date_last_paid",
        "mi_recoveries",
        "net_sales_proceeds",
        "non_mi_recoveries",
        "expenses",
        "legal_costs",
        "maintenance_costs",
        "taxes_and_insurance",
        "misc_expenses",
        "actual_loss_calc",
        "modif_cost"
    ]

    MAPPING = {
        "origin_loans": ORIG_MAPPINGS,
        "monthly_loans": MONTHLY_MAPPINGS
    }

    # WARNING: WILL DELETE OLD LOANS DB IF TRUE
    # If in debug mode, will only insert 1 record from each quarter from each year
    def __init__(self, data_dir, debug=False):
        self.client = MongoClient("mongodb://localhost")
        self.db = self.client.loans
        self.data_dir = data_dir
        self.debug = debug
        if "loans" in self.client.database_names():
            if debug:
                print("Dropping old loans db..")
                self.client.drop_database("loans")
                self._load()
            else:
                print("Loans db exists, not re-loading")
        else:
            self._load()

    def _load(self):
        for f in os.listdir(self.data_dir):
            if f.endswith(".zip"):
                self._load_zip(os.path.join(self.data_dir, f))

    def _insert_file(self, f, col, key):
        buffer = []
        if self.debug:
            lines_to_read = [f.readline()]
            lines_to_read = []
            for i in range(0, 500):
                lines_to_read.append(f.readline())
        else:
            lines_to_read = f.readlines()

        # line = f.readline()
        line_count = 0
        max_lines = 250000
        # while line:
        for line in lines_to_read:
            attribs = line.decode().strip().split("|")
            data = {}
            count = 0
            for attrib in LoanDataLoader.MAPPING[col]:
                data[attrib] = attribs[count]
                count = count + 1

            buffer.append({
                **data,
                "quarter": key[:2],
                "year": key[2:]
            })
            # line = f.readline()
            line_count = line_count + 1
            # if line_count % 1000 == 0:
            #     self.db[col].insert_many(buffer)
            #     buffer = []
            if line_count > max_lines:
                break

        sys.stdout.write("/{}/{}".format(key[:2], line_count / 1000))
        sys.stdout.flush()
        self.db[col].insert_many(buffer)


    def _load_zip(self, zipf):
        archive = zipfile.ZipFile(zipf, 'r')
        sys.stdout.write("Processing " + zipf)
        for qf in archive.filelist:
            data_name = qf.filename.split("_")[-1][:-4].lower()
            q_archive = zipfile.ZipFile(BytesIO(archive.read(qf.filename)), 'r')
            for data_file in q_archive.filelist:
                self._insert_file(q_archive.open(data_file.filename),
                                  "monthly_loans" if data_file.filename.split("_")[2] == "time"
                                  else "origin_loans", data_name)
        sys.stdout.write("\n")
        tw = 2


def main():
    loader = LoanDataLoader("data/", debug=True)
    db = loader.db
    print("Loaded data")


if __name__ == "__main__":
    main()
