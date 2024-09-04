(function($) {
    $(document).ready(function() {
        let selectedIndex = -1;
        const $results = $("#results");
        const $searchBar = $("#search-bar");

        function resetSelectedIndex() {
            selectedIndex = -1;
        }

        function updateSelection() {
            $results.find(".result").removeClass("selected");
            if (selectedIndex !== -1) {
                $($results.find(".result")[selectedIndex]).addClass("selected");
            }
        }

        $searchBar.on("input", function() {
            resetSelectedIndex();
            const query = $(this).val();
            search(query);
        });

        $searchBar.on("keydown", function(e) {
            const results = $results.find(".result");

            if (e.keyCode === 38) { // Up arrow
                e.preventDefault();
                selectedIndex = Math.max(0, selectedIndex - 1);
                updateSelection();
            } else if (e.keyCode === 40) { // Down arrow
                e.preventDefault();
                selectedIndex = Math.min(results.length - 1, selectedIndex + 1);
                updateSelection();
            } else if (e.keyCode === 13) { // Enter key
                e.preventDefault();
                if (selectedIndex !== -1) {
                    results.eq(selectedIndex).trigger("click");
                }
            }
        });

        function search(query) {
            $.post("/search", { query: query }, function(data) {
                displaySearchResults(data);
            });
        }

        function escapeRegExp(string) {
            return string.replace(/[.*+\-?^${}()|[\]\\]/g, '\\$&');
        }

        function displaySearchResults(data) {
            $results.empty();
            if (data.results.length === 0) {
                $results.append('<div class="no-results">No match found</div>').show();
            } else {
                const query = $searchBar.val();
                data.results.forEach(function(result) {
                const resultElement = $("<div></div>")
                    .addClass("result")
                    .html(
                        result.ipAddress
                            ? `${result.name} - ${result.ipAddress.replace(new RegExp('(' + query + ')', 'gi'), '<span class="highlight">$1</span>')}`
                            : result.name.replace(new RegExp('(' + query + ')', 'gi'), '<span class="highlight">$1</span>')
                    )
                    .data("name", result.name)
                    .data("ipAddress", result.ipAddress)
                    .data("ipsForService", result.ipsForService)
                    .on("click", function() {
                        const name = $(this).data("name");
                        const ipAddress = $(this).data("ipAddress") || "N/A";
                        const ipsForService = $(this).data("ipsForService");
                        $("#name").text(name);
                        if (result.ipAddress) {
                            $("#ipAddress").text(ipAddress);
                        } else {
                            if (/^\d+\.\d+\.\d+\.\d+\/\d+$/.test(ipAddress)) {
                                $("#ipAddress").text(ipAddress);
                            } else {
                                $("#ipAddress").text(ipsForService);
                            }
                            // Reset DNS name if there is no IP address
                            $("#dnsName").text("");
                        }
                        $("#results").empty().hide();
                        $("#search-bar").val("");
                    });
                $("#results").append(resultElement);
            });
            $results.show();
        }
    }
});
})(jQuery);