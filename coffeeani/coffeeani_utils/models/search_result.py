class SearchResult:
    """A class representing a manga result instance."""

    def __init__(self):
        """
        Initialize SearchResult with default variables shared across all instances
        """
        self.series_id = None
        self.link = None
        self.title = None
        self.description = None
        self.image = None
        self.image_thumbnail = None
        self.embed_description = None
        self.external_links = None
        self.info_format = None
        self.info_status = None
        self.info_epschaps = None
        self.info_start_end = None
        self.info_start_year = None
        self.info_links = None
        self.info = None
        self.country_of_origin = None
        self.country_of_origin_flag_str = None
        self.relations = None
        self.names = None
        self.tags = None
        self.background_color = None
