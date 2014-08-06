$(document).ready(function() {
    $("article.quote").each(function() {
        var quote_id = $(this).data("quote-id");

        $(this).find("a.vote").each(function() {
            var $voter = $(this);

            $(this).on("click", function() {
                $.ajax({
                    type: "POST",
                    url:  "/vote/" + quote_id,
                    data: {
                        direction: $(this).data("direction")
                    }
                })
                .fail(function() {
                    alert("lol it broke");
                })
                .done(function() {
                    var score = parseInt($voter.siblings(".score").text()) + parseInt($voter.data("direction"));

                    $voter.siblings(".score").text(score);
                });

                return false;
            });
        });
    });
});
