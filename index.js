const express = require('express')
const app = express()
const port = 3000

app.get('/', (req, res) => {
    let fileName = 'home.html',
        options = {
            root: "pages"
        };
    res.sendFile(fileName, options, function (err) {
        if (err) {
            next(err);
        } else {
            console.log('Sent:', fileName);
        }
    });
})

app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
})
