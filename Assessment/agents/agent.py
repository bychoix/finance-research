if __name__ == "__main__":
    while True:
        html = extract_wiley_latest_html("https://onlinelibrary.wiley.com/latest/")
        if html.title != database[-1].title:
            df = parse_wiley_metadata(html)
            response = client.models.generate_content(
                    model='gemini-2.5-flash-lite',
                    contents=
                    f"""
                    extract the background, research_question, data, methods, main_results, implications, whether it is_AI_related
                    """
                    +
                    str(df)
                )
            check_response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=
                f"""
                determine each of the strings in the following list is truly Artificial Intelligence related.
                """
                +
                response
            )
            check_response.to_csv('agent_database.csv', index=False)