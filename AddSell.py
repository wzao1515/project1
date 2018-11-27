#UNDER "Query Average grades for every snack"
server.py
# Query where to buy the snack
        prices = []
        #cursor = g.conn.execute("SELECT * FROM sell")
        cursor = g.conn.execute("WITH tmp AS (SELECT s.m_name, s.bid, s.price, p.location, p.open_time, p.close_tim
e FROM sell AS s LEFT JOIN physicalmarket AS p ON s.m_name = p.m_name) SELECT tmp.bid, tmp.price, CONCAT(tmp.m_name
, ' || ', o.website, '  ', tmp.location, '  ', tmp.open_time, '  ', tmp.close_time)  AS market FROM tmp LEFT JOIN o
nlinemarket AS o ON tmp.m_name = o.m_name")
        prices = cursor.fetchall()
        cursor.close()
        context = dict(snacks=snacks, comments=comments, grades=grades, user_comments=user_comments, prices=prices)
        return render_template("snc.html", **context)

#UNDER "NUTRIENTS"
snc.html
<br>
</br>
<h4> Sold at:</h4>
<table style="width:100%">
<tr>
<th>Price ($)</th>
<th>Market (Name||Website| Location Open(AM) Close(PM))</th>
</tr>
{% for sbid, price, market in prices %}
        {% if bid == sbid %}
        <tr>
        <td>{{price}}</td>
        <td>{{market}}</td>
        </table>
        {% endif %}
{% endfor %}
<br>
</br>