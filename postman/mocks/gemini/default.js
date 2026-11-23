/** Local contract simulation only. This is never a real RAG generation provider. */
const http = require('http');
const server = http.createServer((req, res) => {
  if (req.method !== 'POST' || !/^\/v1beta\/models\/[^/]+:generateContent$/.test(req.url)) {
    res.writeHead(501); return res.end('Not modeled');
  }
  let body = '';
  req.on('data', chunk => { body += chunk; });
  req.on('end', () => {
    try {
      const input = JSON.parse(body);
      if (!req.headers['x-goog-api-key'] || !input.contents || !input.systemInstruction || input.generationConfig.responseMimeType !== 'application/json') {
        res.writeHead(400); return res.end('Invalid contract');
      }
      const prompt = JSON.parse(input.contents[0].parts[0].text);
      if (prompt.question.includes('SIM_ERROR')) {
        res.writeHead(503); return res.end('<html>Upstream unavailable</html>');
      }
      const output = prompt.question.includes('SIM_INVALID') ?
        {answer:'Untrusted fixture',citations:['CBP-S99'],insufficient:false} :
        prompt.question.includes('SIM_UNSUPPORTED') ?
        {answer:'Insufficient evidence in the approved corpus.',citations:[],insufficient:true} :
        {answer:'View Details opens an individual sample build detail page.',citations:[prompt.evidence[0].id],insufficient:false};
      const respond = () => {
        res.writeHead(200, {'Content-Type':'application/json'});
        res.end(JSON.stringify({candidates:[{content:{parts:[{text:JSON.stringify(output)}]}}]}));
      };
      if (prompt.question.includes('SIM_TIMEOUT')) setTimeout(respond, 1000);
      else respond();
    } catch (_) { res.writeHead(400); res.end('Invalid JSON'); }
  });
});
server.listen(process.env.PORT || 4510);
