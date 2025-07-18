from django.shortcuts import render,get_list_or_404,redirect
from django.db import connections
from math import ceil
from .sales_pivot import SalesReportFetches
import pandas as pd
from django.db import connection
from datetime import datetime

def index(request):
    return render(render,'pages/main.html')
# Create your views here.
from django.shortcuts import render
from django.db import connections

def invmovements_view(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 100))
    if per_page > 1000:
        per_page = 1000
    elif per_page < 1:
        per_page = 100

    offset = (page - 1) * per_page

    with connections['SWKD'].cursor() as cursor:
        # Total rows count
        cursor.execute("SELECT COUNT(*) FROM [SysproCompanySWKD].[dbo].[InvMovements]")
        total_rows = cursor.fetchone()[0]
        total_pages = ceil(total_rows / per_page)

        # Paged data
        cursor.execute("""
            SELECT StockCode, Warehouse, TrnQty, TrnValue, EntryDate
            FROM [SysproCompanySWKD].[dbo].[InvMovements]
            ORDER BY EntryDate DESC
            OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
        """, [offset, per_page])

        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    context = {
        'rows': rows,
        'columns': columns,
        'page': page,
        'per_page': per_page,
        'total_rows': total_rows,
        'total_pages': total_pages,
    }
    return render(request, 'pages/test.html', context)

def testmove(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 100))
    search = request.GET.get('search', '').strip()

    if per_page > 1000:
        per_page = 1000
    elif per_page < 1:
        per_page = 100

    offset = (page - 1) * per_page

    # Global search filters
    filters = []
    params = []

    if search:
        filters.append("""
            (StockCode LIKE %s OR
             Warehouse LIKE %s OR
             Reference LIKE %s OR
             LotSerial LIKE %s)
        """)
        for _ in range(4):
            params.append(f"%{search}%")

    where_sql = "WHERE " + " AND ".join(filters) if filters else ""

    with connections['SWKD'].cursor() as cursor:
        # Count rows
        count_sql = f"SELECT COUNT(*) FROM [SysproCompanySWKD].[dbo].[InvMovements] {where_sql}"
        cursor.execute(count_sql, params)
        total_rows = cursor.fetchone()[0]
        total_pages = ceil(total_rows / per_page)

        # Get data
        data_sql = f"""
            SELECT *
            FROM [SysproCompanySWKD].[dbo].[InvMovements]
            {where_sql}
            ORDER BY EntryDate DESC
            OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
        """
        cursor.execute(data_sql, params + [offset, per_page])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    context = {
        'rows': rows,
        'columns': columns,
        'page': page,
        'per_page': per_page,
        'search': search,
        'total_rows': total_rows,
        'total_pages': total_pages,
    }
    return render(request, 'pages/test2.html', context)



def invmovements(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 100))
    search = request.GET.get('search', '').strip()

    if per_page > 1000:
        per_page = 1000
    elif per_page < 1:
        per_page = 100

    offset = (page - 1) * per_page

    # Global search filters
    filters = []
    params = []

    if search:
        filters.append("""
            (StockCode LIKE %s OR
             Warehouse LIKE %s OR
             Reference LIKE %s OR
             LotSerial LIKE %s)
        """)
        for _ in range(4):
            params.append(f"%{search}%")

    where_sql = "WHERE " + " AND ".join(filters) if filters else ""

    with connections['SWKD'].cursor() as cursor:
        # Count rows
        count_sql = f"SELECT COUNT(*) FROM [SysproCompanySWKD].[dbo].[InvMovements] {where_sql}"
        cursor.execute(count_sql, params)
        total_rows = cursor.fetchone()[0]
        total_pages = ceil(total_rows / per_page)

        # Get data
        data_sql = f"""
            SELECT *
            FROM [SysproCompanySWKD].[dbo].[InvMovements]
            {where_sql}
            ORDER BY EntryDate DESC
            OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
        """
        cursor.execute(data_sql, params + [offset, per_page])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    context = {
        'rows': rows,
        'columns': columns,
        'page': page,
        'per_page': per_page,
        'search': search,
        'total_rows': total_rows,
        'total_pages': total_pages,
    }
    return render(request, 'pages/invmovement.html', context)


def sale_analytic(request):
   
    sql_f_sales = SalesReportFetches(min_year=2019)
    df = sql_f_sales.sales_data()
    totalnet = sql_f_sales.net_total_sale(df)
    chartbyyear = sql_f_sales.yearly_sales_list(df)
    latest_month = sql_f_sales.latest_month_sales(df)
    daily_sales = sql_f_sales.latest_month_sales_by_day(df)
    top_customers = sql_f_sales.get_top_customers(df)

    
    years = [entry['year'] for entry in chartbyyear]
    sales = [round(entry['total'] / 1_000_000, 1) for entry in chartbyyear]

    chart_categories = [""]
    chart_data = [0.0]

    for entry in daily_sales:
        dt = datetime.strptime(entry['date'],"%Y-%m-%d")
        chart_categories.append(dt.strftime("%b %d"))
        chart_data.append(round(entry['total'] / 1_000))  # ← thousands with no decimals
    
    chart_categories.append("")
    chart_data.append(0.0)



    context = {
        'years':years,
        'sales':sales,
        'netsale':totalnet,
        'latest_month':latest_month,
        'daily_sales':daily_sales,
        'chart_categories_kt20': chart_categories,
        'chart_data_kt20': chart_data,
        'top_customers': top_customers,
        
    }
    return render(request, 'pages/sales.html', context)


