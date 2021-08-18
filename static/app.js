// axios post to get json data
// async function getJSON() {
//     res = await axios.get("get-characters-quotes");

//     for (i = 0; i < Object.keys(res.data.chars).length; i++){
//         $("#chars-tbody").append(generateCharMarkup(res, i))
//     };
//     for (j = 0; j < Object.keys(res.data.quotes).length; j++){
//         $("#quote-list").append(generateQuoteMarkeup(res, j))
//     };
// };


// // markup generators, hope they work
// function generateCharMarkup(res, num) {
    
//     keys = Object.keys(res.data.chars).sort()

//     if (res.data.chars[keys[num]].realm){
//             return `<tr id=${res.data.chars[keys[num]].id}>
//                 <td scope="col">${res.data.chars[keys[num]].name}</col>
//                 <td scope="col">${res.data.chars[keys[num]].race}</col>
//                 <td scope="col">${res.data.chars[keys[num]].realm}</col>
//             </tr>`}
//     else{
//         return `<tr id=${res.data.chars[keys[num]].id}>
//             <td scope="col">${res.data.chars[keys[num]].name}</col>
//             <td scope="col">${res.data.chars[keys[num]].race}</col>
//             <td scope="col">NA</col>
//         </tr>`}
//     };


// function generateQuoteMarkeup(res, num) {

//     keys = Object.keys(res.data.quotes).sort()

//     return `<li class="list-group-item" id="${res.data.quotes[keys[num]].id}">${res.data.quotes[keys[num]].dialog}</li>`
// };

// $("#char-quote-btn").on("click", function(evt){
//     evt.preventDefault();

//     getJSON();
// });

// I'm leaving this here to let you know i wasted maybe two days making these HTML markup functions work not remembering that the info disappears after a refresh. So its a reminder I'm stupid sorry

$(".char-list-item").on("click", function(evt){
    let id = $(evt)[0].currentTarget.id;
    
    location.href = `http://localhost:5000/characters/${id}`
});

$(".movie").on("click", function(evt){
    let id = $(evt)[0].currentTarget.id;

    location.href = `http://localhost:5000/movies/${id}`
});