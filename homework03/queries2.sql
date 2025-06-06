SELECT e.firstname, e.lastname, d.name AS department
FROM humanresources.employee AS e
JOIN humanresources.employeedepartmenthistory AS h
ON e.businessentityid = h.businessentityid
JOIN humanresources.department AS d
ON h.departmentid = d.departmentid
WHERE e.maritalstatus = 'M';
