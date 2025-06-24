from django.shortcuts import render,get_list_or_404,redirect
from django.db import connections
from math import ceil

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
    sql = """
        SELECT TOP 100
            StockCode,
            Warehouse,
            EntryDate,
            TrnTime,
            MovementType,
            TrnQty,
            TrnValue,
            Reference,
            LotSerial,
            IoProcessedFlag
        FROM [SysproCompanySWKD].[dbo].[InvMovements]
        ORDER BY EntryDate DESC, TrnTime DESC
    """

    with connections['SWKD'].cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in rows]

    return render(request, 'pages/test.html', {'rows': data})



def invmovements_view2(request):
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
        count_sql = f"SELECT COUNT(*) FROM Invmovements {where_sql}"
        cursor.execute(count_sql, params)
        total_rows = cursor.fetchone()[0]
        total_pages = ceil(total_rows / per_page)

        # Get data
        data_sql = f"""
            SELECT StockCode, Warehouse, TrnQty, TrnValue, EntryDate, Reference, LotSerial
            FROM Invmovements
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
    return render(request, 'test2.html', context)