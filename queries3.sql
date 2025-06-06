SELECT departmentid, COUNT(*) AS employee_count
FROM humanresources.employeedepartmenthistory
GROUP BY departmentid
HAVING COUNT(*) > 5;
