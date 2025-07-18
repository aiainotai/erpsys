import pandas as pd
import datetime
from sqlalchemy import create_engine
from django.db import connections

class SalesReportFetches:
    def __init__(self, min_year=2015):
        self.min_year = min_year
        self.engine = create_engine(
            "mssql+pyodbc://cosmo:cosmo@192.168.10.9:1433/SysproCompanySWKD?driver=ODBC+Driver+17+for+SQL+Server"
        )

    
    def sales_data(self):
        sql = f"""
            SELECT
                TD.TrnYear,
                TD.TrnMonth,
                TD.DocumentType,
                TD.Invoice,
                TD.InvoiceDate,
                SD.SalesOrder,
                SD.MLineShipDate,
                TD.Customer,
                AC.Name AS [Customer.Name],
                SM.CustomerPoNumber,
                SM.ShipAddress4,
                SM.ShipAddress5,
                TD.Salesperson,
                TD.StockCode,
                SD.MStockDes,
                TD.Warehouse,
                TD.ProductClass,
                SPD.Description AS [Prod. Class Description],
                TD.QtyInvoiced,
                SM.Currency,
                TD.PostValue,
                TD.PostConvRate,
                TD.CostValue,
                SD.MTaxCode,
                TD.TaxValue,
                TD.NetSalesValue,
                TD.TransactionGlCode,
                TD.CostGlCode,
                SD.NComment
            FROM
                [SysproCompanySWKD].[dbo].[ArTrnDetail] TD
            JOIN
                [SysproCompanySWKD].[dbo].[SorMaster] SM ON TD.SalesOrder = SM.SalesOrder
            JOIN
                [SysproCompanySWKD].[dbo].[ArCustomer] AC ON TD.Customer = AC.Customer
            JOIN
                [SysproCompanySWKD].[dbo].[SorDetail] SD ON TD.SalesOrder = SD.SalesOrder AND TD.SalesOrderLine = SD.SalesOrderLine
            JOIN
                [SysproCompanySWKD].[dbo].[SalProductClassDes] SPD ON TD.ProductClass = SPD.ProductClass
            WHERE
                TD.Warehouse <> '**' AND TD.Warehouse <> ''
                AND TD.TrnYear > {self.min_year}
                AND TD.Invoice NOT IN (
                   'SW-TRO-25-00031', 'SW-TRI-25-00224', 'SW-TRI-25-00225', 'SW-TRI-25-00226', 'SW-TRI-25-00250', 
                    'SW-TRI-25-00251', 'SW-TRO-25-00032', 'SW-TRI-25-00177', 'SW-TRI-25-00179', 'SW-TRI-25-00180', 
                    'SW-TRI-25-00185', 'SW-TRI-25-00195', 'SW-TRI-25-00212', 'SW-TRI-25-00241', 'SW-TRI-25-00219', 
                    'SW-TRI-25-00221', 'SW-TRI-25-00222', 'SW-TRI-25-00223', 'SW-TRI-25-00227', 'SW-TRI-25-00228', 
                    'SW-TRI-25-00229', 'SW-TRI-25-00230', 'SW-TRI-25-00231', 'SW-TRI-25-00232', 'SW-TRI-25-00233', 
                    'SW-TRI-25-00234', 'SW-TRI-25-00235', 'SW-TRI-25-00239', 'SW-TRI-25-00240', 'SW-TRI-25-00242', 
                    'SW-TRI-25-00244', 'SW-TRI-25-00245', 'SW-TRI-25-00246', 'SW-TRI-25-00247', 'SW-TRI-25-00248', 
                    'SW-TRI-25-00249', 'SW-TRI-25-00252', 'SW-TRI-25-00253', 'SW-TRI-25-00178', 'SW-TRI-25-00181', 
                    'SW-TRI-25-00182', 'SW-TRI-25-00183', 'SW-TRI-25-00184', 'SW-TRI-25-00186', 'SW-TRI-25-00187', 
                    'SW-TRI-25-00188', 'SW-TRI-25-00189', 'SW-TRI-25-00190', 'SW-TRI-25-00191', 'SW-TRI-25-00192', 
                    'SW-TRI-25-00193', 'SW-TRI-25-00194', 'SW-TRI-25-00196', 'SW-TRI-25-00197', 'SW-TRI-25-00198', 
                    'SW-TRI-25-00199', 'SW-TRI-25-00200', 'SW-TRI-25-00201', 'SW-TRI-25-00202', 'SW-TRI-25-00203', 
                    'SW-TRI-25-00204', 'SW-TRI-25-00205', 'SW-TRI-25-00206', 'SW-TRI-25-00207', 'SW-TRI-25-00208', 
                    'SW-TRI-25-00209', 'SW-TRI-25-00210', 'SW-TRI-25-00211', 'SW-TRI-25-00213', 'SW-TRI-25-00214', 
                    'SW-TRI-25-00215', 'SW-TRI-25-00216', 'SW-TRI-25-00217', 'SW-TRI-25-00218', 'SW-TRI-25-00220', 
                    'SW-TRI-25-00236', 'SW-TRI-25-00237', 'SW-TRI-25-00238', 'SW-TRI-25-00243', 'SW-TRI-25-00254'
                )
        """

        return pd.read_sql(sql, self.engine)
    
    def net_total_sale(self, df):
        return df['NetSalesValue'].sum()

        
    
    def yearly_sales_list(self,df):
        grouped = (
            df.groupby('TrnYear')['NetSalesValue']
            .sum()
            .reset_index()
            .rename(columns={'TrnYear': 'year', 'NetSalesValue': 'total'})
        )
        return grouped.to_dict(orient='records')
    
    
    def latest_month_sales(self, df):
        
        current_year = datetime.datetime.now().year

        # Try current year first
        current_year_df = df[df['TrnYear'] == current_year]
        if not current_year_df.empty:
            latest_month = current_year_df['TrnMonth'].max()
            latest_df = current_year_df[current_year_df['TrnMonth'] == latest_month]
            total = latest_df['NetSalesValue'].fillna(0).sum()
            return {
                'year': current_year,
                'month': latest_month,
                'total': total
            }

        # 🔁 Fallback: 2024 Augus
        fallback_df = df[(df['TrnYear'] == 2023) & (df['TrnMonth'] == 6)]
        if not fallback_df.empty:
            total = fallback_df['NetSalesValue'].fillna(0).sum()
            return {
                'year': 2023,
                'month': 6,
                'total': total
            }

        # 🛑 If nothing found
        return None
    

    def latest_month_sales_by_day(self, df):

        latest = self.latest_month_sales(df)  # this uses fallback to 2024-Aug if 2025 is missing

        if not latest:
            return []

         # Filter the DataFrame for the fallback month
        filtered_df = df[
            (df['TrnYear'] == latest['year']) &
            (df['TrnMonth'] == latest['month'])
        ]

        # Group by invoice date (daily sales)
        daily = (
            filtered_df.groupby('InvoiceDate')['NetSalesValue']
            .sum()
            .reset_index()
            .sort_values('InvoiceDate')
        )

        # Convert date format to YYYY-MM-DD
        daily['InvoiceDate'] = daily['InvoiceDate'].dt.strftime('%Y-%m-%d')

        return daily.rename(columns={
            'InvoiceDate': 'date',
            'NetSalesValue': 'total'
        }).to_dict(orient='records')
    

    def get_top_customers(self, df, limit=10):
        top = (
            df.groupby('Customer.Name')['NetSalesValue']
            .sum()
            .reset_index()
            .sort_values('NetSalesValue', ascending=False)
            .head(limit)
        )

        top['NetSalesValue'] = top['NetSalesValue'].round(2)

        return top.rename(columns={
           
            'Customer.Name': 'customer',
            'NetSalesValue': 'total'
        }).to_dict(orient='records')



    
    

