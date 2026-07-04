const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// SQLite baza
const db = new sqlite3.Database('./buses.db');

// Kreiraj tablicu
db.run(`
  CREATE TABLE IF NOT EXISTS bus_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    garage_number TEXT NOT NULL,
    line_name TEXT,
    status TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

// Početna stranica
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>🚌 Povijest autobusa Split</title>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        * { box-sizing: border-box; }
        body { 
          font-family: Arial, sans-serif; 
          padding: 20px; 
          background: #0f0f1a; 
          color: #e0e0e0;
          margin: 0;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { 
          color: #ff6600; 
          border-bottom: 2px solid #ff6600;
          padding-bottom: 10px;
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .stats {
          display: flex;
          gap: 20px;
          flex-wrap: wrap;
          margin: 20px 0;
        }
        .stat-box {
          background: #1a1a2e;
          padding: 12px 24px;
          border-radius: 12px;
          border: 1px solid #333;
        }
        .stat-box span { color: #ff6600; font-weight: bold; font-size: 20px; }
        .search-box {
          display: flex;
          gap: 10px;
          margin: 20px 0;
          flex-wrap: wrap;
        }
        .search-box input {
          padding: 12px 20px;
          border-radius: 30px;
          border: 1px solid #333;
          background: #1a1a2e;
          color: white;
          flex: 1;
          min-width: 200px;
          font-size: 14px;
        }
        .search-box input:focus { outline: 2px solid #ff6600; border: none; }
        .search-box button {
          padding: 12px 24px;
          border-radius: 30px;
          border: none;
          background: #ff6600;
          color: white;
          font-weight: bold;
          cursor: pointer;
        }
        .search-box button:hover { background: #ff5500; }
        .table-wrap {
          overflow-x: auto;
          background: #1a1a2e;
          border-radius: 12px;
          border: 1px solid #333;
          padding: 10px;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          font-size: 14px;
        }
        th {
          background: #2a2a4e;
          color: #ff6600;
          padding: 12px;
          text-align: left;
          position: sticky;
          top: 0;
        }
        td {
          padding: 10px 12px;
          border-bottom: 1px solid #2a2a3e;
        }
        tr:hover { background: #2a2a3e; }
        .active { color: #4CAF50; font-weight: bold; }
        .inactive { color: #ff4444; font-weight: bold; }
        .badge {
          display: inline-block;
          padding: 3px 10px;
          border-radius: 20px;
          font-size: 11px;
          font-weight: bold;
        }
        .badge-active { background: #1b5e20; color: #a5d6a7; }
        .badge-inactive { background: #b71c1c; color: #ef9a9a; }
        .footer {
          text-align: center;
          margin-top: 30px;
          color: #666;
          font-size: 12px;
        }
        .live-dot {
          display: inline-block;
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: #4CAF50;
          animation: pulse 1.5s infinite;
          margin-right: 8px;
        }
        @keyframes pulse {
          0% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(0.8); }
          100% { opacity: 1; transform: scale(1); }
        }
        .empty { text-align: center; padding: 40px; color: #666; }
        .clear-btn {
          background: #d32f2f;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 20px;
          cursor: pointer;
          font-size: 12px;
          margin-left: 10px;
        }
        .clear-btn:hover { background: #b71c1c; }
        @media (max-width: 600px) {
          body { padding: 10px; }
          .stat-box { padding: 8px 16px; font-size: 12px; }
          .stat-box span { font-size: 16px; }
          td, th { padding: 6px 8px; font-size: 12px; }
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>
          <span class="live-dot"></span>
          🚌 Povijest autobusa Split
          <button class="clear-btn" onclick="clearHistory()">🗑️ Obriši povijest</button>
        </h1>
        
        <div class="stats" id="stats">
          <div class="stat-box">📊 Ukupno: <span id="totalBuses">0</span></div>
          <div class="stat-box">✅ Aktivni: <span id="activeBuses">0</span></div>
          <div class="stat-box">❌ Neaktivni: <span id="inactiveBuses">0</span></div>
        </div>

        <div class="search-box">
          <input type="text" id="searchInput" placeholder="🔍 Pretraži po garažnom broju ili liniji..." onkeyup="filterTable()">
          <button onclick="loadData()">🔄 Osvježi</button>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Garažni broj</th>
                <th>Linija</th>
                <th>Status</th>
                <th>Vrijeme</th>
              </tr>
            </thead>
            <tbody id="tableBody">
              <tr><td colspan="4" class="empty">⏳ Učitavanje podataka...</td></tr>
            </tbody>
          </table>
        </div>
        <div class="footer">
          ⏱️ Ažurirano: <span id="lastUpdate">-</span> | Server radi 24/7 i pamti sve promjene
        </div>
      </div>

      <script>
        async function loadData() {
          try {
            const res = await fetch('/api/history');
            const data = await res.json();
            const tbody = document.getElementById('tableBody');
            
            if (data.length === 0) {
              tbody.innerHTML = '<tr><td colspan="4" class="empty">📭 Još nema podataka</td></tr>';
              return;
            }

            // Statistika
            const active = data.filter(r => r.status === 'active').length;
            const inactive = data.filter(r => r.status === 'inactive').length;
            document.getElementById('totalBuses').textContent = data.length;
            document.getElementById('activeBuses').textContent = active;
            document.getElementById('inactiveBuses').textContent = inactive;

            tbody.innerHTML = data.map(row => {
              const statusClass = row.status === 'active' ? 'active' : 'inactive';
              const badgeClass = row.status === 'active' ? 'badge-active' : 'badge-inactive';
              const statusText = row.status === 'active' ? '✅ U prometu' : '❌ Nije u prometu';
              const time = new Date(row.timestamp).toLocaleString('hr-HR', {
                day: '2-digit', month: '2-digit', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
              });
              return \`
                <tr>
                  <td><strong>\${row.garage_number}</strong></td>
                  <td>\${row.line_name || '-'}</td>
                  <td><span class="badge \${badgeClass}">\${statusText}</span></td>
                  <td>\${time}</td>
                </tr>
              \`;
            }).join('');

            document.getElementById('lastUpdate').textContent = new Date().toLocaleString('hr-HR');

          } catch (e) {
            document.getElementById('tableBody').innerHTML = '<tr><td colspan="4" class="empty">❌ Greška pri učitavanju</td></tr>';
          }
        }

        function filterTable() {
          const search = document.getElementById('searchInput').value.toLowerCase();
          const rows = document.querySelectorAll('#tableBody tr');
          rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(search) ? '' : 'none';
          });
        }

        async function clearHistory() {
          if (!confirm('Sigurno želiš obrisati svu povijest?')) return;
          try {
            await fetch('/api/clear', { method: 'POST' });
            loadData();
          } catch(e) { alert('Greška pri brisanju'); }
        }

        loadData();
        setInterval(loadData, 10000);
      </script>
    </body>
    </html>
  `);
});

// API - povijest (zadnjih 500)
app.get('/api/history', (req, res) => {
  db.all(`
    SELECT * FROM bus_history 
    ORDER BY timestamp DESC 
    LIMIT 500
  `, (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

// API - brisanje povijesti
app.post('/api/clear', (req, res) => {
  db.run(`DELETE FROM bus_history`, (err) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ success: true });
  });
});

// Provjera autobusa
async function checkBuses() {
  try {
    const response = await fetch('https://www.bus-split.com/api/vehicles/live');
    const data = await response.json();
    
    if (!data.vehicles) return;
    
    const activeBuses = data.vehicles.map(v => v.garageNumber);
    
    // Dohvati sve poznate autobuse iz baze
    db.all(`SELECT DISTINCT garage_number FROM bus_history`, (err, rows) => {
      if (err) return;
      
      const knownBuses = rows.map(r => r.garage_number);
      const allBuses = new Set([...knownBuses, ...activeBuses]);
      
      allBuses.forEach(gbr => {
        const isActive = activeBuses.includes(gbr);
        const bus = data.vehicles.find(v => v.garageNumber === gbr);
        const line = bus ? bus.name : null;
        const newStatus = isActive ? 'active' : 'inactive';
        
        // Dohvati zadnji status
        db.get(`
          SELECT status FROM bus_history 
          WHERE garage_number = ? 
          ORDER BY timestamp DESC 
          LIMIT 1
        `, [gbr], (err, lastRow) => {
          if (err) return;
          
          const lastStatus = lastRow?.status;
          
          // Spremi samo ako se status promijenio ILI je prvi put
          if (lastStatus !== newStatus || !lastRow) {
            db.run(`
              INSERT INTO bus_history (garage_number, line_name, status)
              VALUES (?, ?, ?)
            `, [gbr, line, newStatus]);
            console.log(\`📝 \${gbr}: \${newStatus} (\${line || 'nepoznato'})\`);
          }
        });
      });
    });
  } catch (error) {
    console.error('Greška:', error.message);
  }
}

// Pokreni server
app.listen(PORT, () => {
  console.log(\`🚌 Server radi na portu \${PORT}\`);
  checkBuses();
  setInterval(checkBuses, 15000);
});