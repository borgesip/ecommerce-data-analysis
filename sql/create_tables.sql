DROP TABLE IF EXISTS sales;
CREATE TABLE sales (
    invoiceno VARCHAR(20),
    stockcode VARCHAR(20),
    description TEXT,
    quantity INT,
    invoicedate TIMESTAMP,
    unitprice FLOAT,
    customerid VARCHAR(20),
    country VARCHAR(50),
    totalvalue FLOAT
);
