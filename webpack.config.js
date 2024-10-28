const path = require('path');

// Define the array of entry files
const arr = ['./backend/src/calender.js',]; // Add more entries as needed

// Convert the array into an entry object, with each entry having a custom filename
const entry = arr.reduce((acc, filePath) => {
    const name = path.basename(filePath, path.extname(filePath)); // Get filename without extension
    acc[name] = filePath;
    return acc;
}, {});
console.log(entry);
module.exports = {
    entry,
    output: {
        filename: '[name].bundle.js', // Use [name] to dynamically replace with each entry key
        path: path.resolve(__dirname, 'backend', 'static_cdn', 'dist')
    }
};
