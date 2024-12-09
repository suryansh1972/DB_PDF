import psycopg2
from fpdf import FPDF
import click


class DataBaseAuto:
    def __init__(self, host, dbname, user, password, port):
        try:
            self.conn = psycopg2.connect(
                host=host, dbname=dbname, user=user, password=password, port=port
            )
        except Exception as e:
            print(f"Failed to connect to the database: {e}")
            self.conn = None

    def db_table_reader(self):
        if self.conn:
            try:
                curr = self.conn.cursor()
                curr.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                    """
                )
                tables = curr.fetchall()
                print("Tables in the database:")
                for table in tables:
                    print(table[0])
                curr.close()
            except Exception as e:
                print(f"Error reading tables: {e}")
        else:
            print("Connection is not established.")

    def db_table_to_pdf(self, table_name, output_file):
        if self.conn:
            try:
                cur = self.conn.cursor()

                # Fetch table columns
                cur.execute(
                    f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}';
                    """
                )
                columns = [col[0] for col in cur.fetchall()]

                # Fetch table rows
                cur.execute(f"SELECT * FROM {table_name};")
                rows = cur.fetchall()

                # Create a PDF
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                # Title
                pdf.set_font("Arial", style="B", size=14)
                pdf.cell(200, 10, txt=f"Table: {table_name}", ln=True, align="C")
                pdf.ln(10)

                # Column headers
                pdf.set_font("Arial", style="B", size=10)
                for col in columns:
                    pdf.cell(40, 10, col, border=1, align="C")
                pdf.ln()

                # Rows
                pdf.set_font("Arial", size=10)
                for row in rows:
                    for cell in row:
                        pdf.cell(40, 10, str(cell), border=1, align="C")
                    pdf.ln()

                # Save the PDF
                pdf.output(output_file)
                print(f"PDF saved as {output_file}")

                cur.close()
            except Exception as e:
                print(f"Error converting table to PDF: {e}")
        else:
            print("Connection is not established.")

    def close_connection(self):
        self.conn.close()


@click.group()
def cli():
    pass

@cli.command()
@click.option("--host", required=True, help="Database host")
@click.option("--dbname", required=True, help="Database name")
@click.option("--user", required=True, help="Database username")
@click.option("--password", required=True, help="Database password")
@click.option("--port", default=5432, help="Database port")
def list_tables(host, dbname, user, password, port):
    db = DataBaseAuto(host, dbname, user, password, port)
    db.db_table_reader()
    db.close_connection()

@cli.command()
@click.option("--host", required=True, help="Database host")
@click.option("--dbname", required=True, help="Database name")
@click.option("--user", required=True, help="Database username")
@click.option("--password", required=True, help="Database password")
@click.option("--port", default=5432, help="Database port")
@click.option("--table_name", required=True, help="Table name to export")
@click.option("--output_file", required=True, help="Output PDF file name")
def export_table(host, dbname, user, password, port, table_name, output_file):
    db = DataBaseAuto(host, dbname, user, password, port)
    db.db_table_to_pdf(table_name, output_file)
    db.close_connection()


if __name__ == "__main__":
    cli()