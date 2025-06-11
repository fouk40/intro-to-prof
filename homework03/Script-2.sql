SELECT 
    p.Name AS ProductName,
    sod.OrderQty,
    sod.UnitPrice,
    (sod.OrderQty * sod.UnitPrice * (1 - sod.UnitPriceDiscount)) AS LineTotal
FROM 
    sales.salesorderheader soh
    INNER JOIN sales.salesorderdetail sod ON soh.SalesOrderID = sod.SalesOrderID
    INNER JOIN production.product p ON sod.ProductID = p.ProductID
WHERE 
    soh.CustomerID = 29825
ORDER BY 
    (sod.OrderQty * sod.UnitPrice * (1 - sod.UnitPriceDiscount)) DESC;