const express = require('express')
const multer = require('multer')
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/')
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9)
        cb(null, file.fieldname + '-' + uniqueSuffix + '.ogg')
    }
})
const upload = multer({ dest: 'uploads/', preservePath: true, storage })
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

app.post('/audio', upload.single('audio'), (req, res) => {
    console.log(req.file);
    res.sendStatus(200);
})

app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
})
