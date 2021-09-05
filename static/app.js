// handle click movie element to go to movie page
$(".movie").on("click", function(evt){
    let id = $(evt)[0].currentTarget.id;

    location.href = `/movies/${id}`
});

// handle click char table row element on table to go to char page
$(".char-list-item").on("click", function(evt){
    let id = $(evt)[0].currentTarget.id;
    
    for (let i =0; i < $("button").length; i++){
        if (evt.target == $("button")[i]){
        return
    }};
    
    location.href = `/characters/${id}`
});

// handle click blockquote direct to quote page
$(".quote").on("click", function(evt){

    let id = $(evt)[0].currentTarget.id;

    for (let i =0; i < $("button").length; i++){
        if (evt.target == $("button")[i]){
        return
    }};

    location.href = `/quotes/${id}`
})

// // when api is called hide button and show loading sign
// function loading(){
//     $("#loading").show();
//     $(".content").hide();
// }

// // call loading after triggering retrieval of character and quote api info
// $("#char-quote-btn").on("click", function(){
//     loading();
// });

// Click handler for favoriting and unfavoriting quotes
$(".like-quote").on("click", "button", async function(evt){
    evt.preventDefault();

    let id = $(evt)[0].currentTarget.dataset.id;
    let divId = id.substring(id.length - 4);

    let res = await axios.post(`/users/fav_quote/${id}`);

    if (res.data.action[1] == 'like'){
        $(`#${divId}`).empty();

        $(`#${divId}`).append(
            `<button class="btn btn-info text-white" data-id="${id}">Unlike</button>`
        )}

    else if (res.data.action[1] == 'unlike'){
        $(`#${divId}`).empty();
        
        $(`#${divId}`).append(
            `<button class="btn btn-info" data-id="${id}">Like</button>`
        )}
    
});

// Click handler for favoriting and unfavoriting characters
$(".like-char").on("click", "button", async function(evt){
    evt.preventDefault();

    let id = $(evt)[0].currentTarget.dataset.id;
    let divId = id.substring(id.length - 5);

    let res = await axios.post(`/users/fav_char/${id}`);

    if (res.data.action[1] == 'like'){
        $(`#${divId}`).empty();

        $(`#${divId}`).append(
            `<button class="btn btn-info text-white" data-id="${id}">Unlike</button>`
        )}

    else if (res.data.action[1] == 'unlike'){
        $(`#${divId}`).empty();
        
        $(`#${divId}`).append(
            `<button class="btn btn-info" data-id="${id}">Like</button>`
        )}
    
});

// Click handler to pull random quotes from database and append onto homepage
$("#random-btn").on("click", async function(evt){
    evt.preventDefault();
    $("#random-quotes").empty();

    let res = await axios.get("/random");

    for (let i=0; i < Object.keys(res.data.quotes).length; i++){        
        $("#random-quotes").append(
            `<div class="col-md-6">
                <div class="card quote my-3" id="${res.data.quotes[i].id}">
                    <div class="card-body">
                        <blockquote class="blockquote">
                            <p>${res.data.quotes[i].dialog}</p>
                            <footer class="blockquote-footer">
                                <a href="/characters/${res.data.quotes[i].char_id}">${res.data.quotes[i].char}</a>
                            </footer>
                        </blockquote>
                    </div>
                </div>
            </div>`
        )
    }
});

// I tried putting the like and comment buttons on, but they required jinja so I couldn't. Until I learn a way, this way it will stay.

$("#random-quotes").on("click", "div.quote", function(evt){
    id = $(evt)[0].currentTarget.id

    location.href = `/quotes/${id}`
});

// i think i can do it


// pagination
function getPageList(totalPages, page, maxLength) {
    function range(start, end){
        return Array.from(Array(end - start + 1), (_, i) => i + start);
    }

    let sideWidth = maxLength < 9 ? 1 : 2;
    let leftWidth = (maxLength - sideWidth * 2 - 3) >> 1;
    let rightWidth = (maxLength - sideWidth * 2 - 3) >> 1;

    if (totalPages <= maxLength) {
        return range(1, totalPages);
    };

    if (page <= maxLength - sideWidth - 1 - rightWidth){
        return range(1, maxLength - sideWidth - 1).concat(0, range(totalPages - sideWidth + 1, totalPages));
    };

    if (page >= totalPages - sideWidth - 1 - rightWidth){
        return range(1, sideWidth).concat(0, range(totalPages - sideWidth - 1 - rightWidth - leftWidth, totalPages));
    };

    return range(1, sideWidth).concat(0, range(page - leftWidth, page + rightWidth), 0, range(totalPages - sideWidth + 1, totalPages));

}

$(function(){
    let numberOfItems = $(".content .item").length;
    let limitPerPage = 6;
    let totalPages = Math.ceil(numberOfItems / limitPerPage);
    let paginationSize = 7;
    let currentPage;

    function showPage(whichPage){
        if (whichPage < 1 || whichPage > totalPages) return false;

        currentPage = whichPage;

        $(".content .item").hide().slice((currentPage - 1) * limitPerPage, currentPage * limitPerPage).show();

        $(".pagination li").slice(1, -1).remove();

        getPageList(totalPages, currentPage, paginationSize).forEach(item => {
            $("<li>").addClass("page-item").addClass(item ? "current-page" : "dots")
            .toggleClass("active", item === currentPage).append($("<a>").addClass("page-link")
            .attr({href: "javascript:void(0)"}).text(item || "...")).insertBefore(".next-page");
        });

        $(".previous-page").toggleClass("disabled", currentPage === 1);
        $(".next-page").toggleClass("disabled", currentPage === totalPages);
        return true;            
    }

    $(".pagination").append(
        $("<li>").addClass("page-item").addClass("previous-page").append($("<a>").addClass("page-link").attr({href: "javascript:void(0)"}).text("Prev")),
        $("<li>").addClass("page-item").addClass("next-page").append($("<a>").addClass("page-link").attr({href: "javascript:void(0)"}).text("Next"))
    );
    
    $(".item").show();
    showPage(1);

    $(".pagination").on("click", "li.current-page:not(.active)", function(){
        return showPage(+$(this).text());
    });

    $(".next-page").on("click", function(){
        return showPage(currentPage + 1);
    });

    $(".previous-page").on("click", function(){
        return showPage(currentPage - 1);
    });
});

