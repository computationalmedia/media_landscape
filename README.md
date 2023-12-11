# Media Landscape

Codes and data for **The Shapes of the Fourth Estate During the Pandemic: Profiling COVID-19 News Consumption in Eight Countries** (CSCW'23)

# Table of Contents
- [Media Landscape](#media-landscape)
- [Table of Contents](#table-of-contents)
- [Data](#data)
- [Section 3 A New COVID2020 Tweet Dataset](#section-3-a-new-covid2020-tweet-dataset)
- [Section 4 Extracting User Geolocation, Political Leaning, and Shared Media Domains](#section-4-extracting-user-geolocation-political-leaning-and-shared-media-domains)
  - [Section 4.1 Extracting Geolocation from Geotagged Tweets and User Profiles](#section-41-extracting-geolocation-from-geotagged-tweets-and-user-profiles)
  - [Section 4.2 Estimating User Political Leaning from Within-Country User-User Retweet Networks](#section-42-estimating-user-political-leaning-from-within-country-user-user-retweet-networks)
  - [Section 4.3 Extracting Shared Media Domains from the Embedded URLs](#section-43-extracting-shared-media-domains-from-the-embedded-urls)
- [Section 5: Results](#section-5-results)
  - [Section 5.1 Distribution of User Political Leaning in Each Country](#section-51-distribution-of-user-political-leaning-in-each-country)
  - [Section 5.2 An Analysis of the Bridging Users](#section-52-an-analysis-of-the-bridging-users)
  - [Section 5.3 A New Media Bias Score by Average Audience Leaning](#section-53-a-new-media-bias-score-by-average-audience-leaning)
  - [Section 5.4 Profiling Cross-Country COVID-19 News Consumption](#section-54-profiling-cross-country-covid-19-news-consumption)


# Data

The data output of this work:

- COVID2020: To comply with Twitter’s content redistribution policy, we only release the tweet IDs of the collected tweets. Our dataset can be downloaded on [SOMAR](https://socialmediaarchive.org/record/51), containing 999,040,035 tweet IDs. Details of our dataset can be found in the paper. Reproduction of results requires re-collection of these tweets, and the full data shall be left under `COVID2020/` folder (assuming each file is named by date).

- Politician list: we release curated politician lists in the eight selected countries, along with each politician’s name, party affiliation, political position, Twitter accounts, and corresponding Wikidata page (if available). It can be found under `Data/Sec_4_2_Label_Spreading/Politician_Collection/`.

- Wikidata query: we also release the Wikidata SPARQL queries used for fetching Twitter handles of governors and legislators. It can be found under `Data/Sec_4_2_Label_Spreading/Wikidata_Query/`.

- Media domain audience reach & bias score: we also release the audience reach metrics and average audience leaning scores for all media domains as computed in Section 5.3 in the paper. It can be found under `Data/Sec_5_3_Media_Domain_Bias/domain_bias.csv`.


# Section 3 A New COVID2020 Tweet Dataset

In section 3, we calculate some basic stats of the dataset. Codes are under `Sec_3_COVID2020/`, where the prefix indicate the order that scripts should be run. Related data files can be found/saved at `Data/Sec_3_COVID2020/`. Ones should first copy the Twitter dataset from [Chen et al.](https://github.com/echen102/COVID-19-TweetIDs) into `Data/Sec_3_COVID2020/COVID-19-TweetIDs/` before starting.

Figure 1 from the paper can be reproduced using `3_figure_1.py` at the end.

# Section 4 Extracting User Geolocation, Political Leaning, and Shared Media Domains

In section 4, there are three subsections here covering geolocation extraction, political leaning estimation, and URL-sharing extraction. 

## Section 4.1 Extracting Geolocation from Geotagged Tweets and User Profiles

Codes for geolocation extraction can be found under `Sec_4_1_Geolocation/`, and related data files can be found under `Data/Sec_4_1_Geolocation/`.

Geolocation extraction contains two steps: geotagging and geoparsing. Geotagging is done by running `1_geotag_extraction.py` and `2_geotag_process.py`, and geoparsing is done by running `3_location_process.py` and `4_geoparse.py`. After obtaining locations, we then map users to their corresponding locations (`5_map_uid_to_loc.py`) and then merge geotagging and geoparsing results (`6_merge_geotag_geoparse.py`) to obtain a list of users with geolocations. `6_merge_geotag_geoparse.py` also contains validation of geoparsing against geotagging. Additionally, we have collected politicians' information in this paper, including their locations. We add these politicians to the list of users with geolocations (`7_add_politicians_to_geolocation.py`). After having users' locations, we further iterate COVID2020 to obtain the language stats of tweets posted by users from different countries (`8_lang_stat.py`).

Figure 2 in the paper can be reproduced using `9_figure_2a.py` and `9_figure_2b.py`.

## Section 4.2 Estimating User Political Leaning from Within-Country User-User Retweet Networks

Codes for retweet network extraction and label spreading can be found under `Sec_4_2_Label_Spreading/`, and related data files can be found under `Data/Sec_4_1_Geolocation/` and `Data/Sec_4_2_Label_Spreading/`.

Label spreading requires both seed users and a network for propagation. We first convert our collected politicians' information (`Data/Sec_4_1_Geolocation/Politicians/`) into seed users within the eight selected countries. This is done using the manually-labeled political party from `Data/Sec_4_2_Label_Spreading`. Next, we construct the within-country retweet network by first collecting retweets across 16 periods (`2_retweet_net_extraction.py`) and then merging them into one single network (`3_retweet_net_merge.py`) for each country. After that, we perform disparity filtering on the constructed network to keep the backbone graph only (`4_nodes_pred_succ.py`, `5_disparity_filter.py` and `6_prep_ls.py`). In the end, we perform cross-validation and prediction using label spreading (`7_label_spreading_cv.py`, `8_label_spreading_prediction.py`).

Additionally, in the paper, we verify the politician-based approach v.s. keyword-based approach for seed users and subsequent political leaning estimation in the United States. For the latter, a list of left and right hashtags is required to identify seed users, which can be found under `Data/Sec_4_2_Label_Spreading/`. Subsequent steps are identical, except we need to check users' profiles for hashtag occurrence while extracting the retweet network. `Sec_4_2_Label_Spreading/9_retweet_net_from_keywords.py` can be used as a reference. Other steps are skipped here, but they can be easily reproduced using the same set of scripts with minimum changes.


## Section 4.3 Extracting Shared Media Domains from the Embedded URLs

Codes for extracting URLs shared on Twitter can be found under `Sec_4_2_Label_Spreading/`, and related data files can be found under `Data/Sec_4_3_URL_Extraction/`.

We first extract URLs shared by Twitter users from the eight selected countries (`1_url_extraction.py`). After that, we iterate through collected URLs to find out shortened URLs by making use of a list of shortened domains (`2_gather_redirected_urls.py`). We further redirect URLs to expand shortened URLs (`3_url_redirection.py`). In the end, for each country, we merge URLs across different periods into one single file (`4_url_processing.py`). We also provide our processed redirected URLs (`Data/Sec_4_3_URL_Extraction/urls_redirected.pickle`) if one wants to skip steps 2 and 3 above.


# Section 5: Results

In section 5, there are four subsections here covering ridge plots, bridging users analysis, media bias score estimation, and cross-country news consumption.

## Section 5.1 Distribution of User Political Leaning in Each Country

Figure 3 in the paper can be reproduced by `Sec_5_1_User_Leaning_by_Country/1_figure_3.py`

## Section 5.2 An Analysis of the Bridging Users

Codes for bridging users analysis can be found under `Sec_5_2_Bridging_Users/`, and related data files can be found under `Data/Sec_5_2_Bridging_Users/`.

Identifying bridging users across countries first requires extracting the retweet network globally (`1_gloabl_retweet_net_extraction.py`). After extracting the retweet network, one must repeat the label spreading process (see `1.5_retweet_net_process` for details). Next, we find bridging users with cross-country retweets (`2_identify_bridging_users.py`). Then we repeat label spreading on the within-country retweet network by adding these users to the network (`3_label_spreading_with_bridging_users.py`). We now have two sets of political leaning estimations for bridging users using two different retweet networks. We can generate figure 4 (density plot) in the paper (`4_figure_4.py`).


## Section 5.3 A New Media Bias Score by Average Audience Leaning

This section covers our own media bias score and comparison with existing work. Codes can be found under `Sec_5_2_Bridging_Users`, and data files can be found under `Data/Sec_5_3_Media_Domain_Bias`.

To compare media bias scores in the United States, one must prepare media bias ratings from Media Bias/Fact Check and AllSides by crawling them from the websites. One must also use the bias scores from [Robertson et al.](https://dl.acm.org/doi/10.1145/3274417). The websites are evolving with time, and hence the scraped results are likely to change. We provide processed files in the corresponding data folder, which are further processed by `utils/domain_bias_from_robertson.py`

For comparison with media bias scores internationally, one needs to obtain online audience political leaning score from [Fletcher et al.](https://ora.ox.ac.uk/objects/uuid:d6b9a202-9a1c-41f7-881e-08256178aeb7/files/swp988j97f) We also provided these data in `utils/domain_bias_from_fletcher.py`.

After obtaining these scores, we can generate correlation plots in the paper (figure 6 and 7) by `3_figure_6.py` and `4_figure_7.py`. Pearson/Spearman correlation coefficients, p-values, and overlapped domains can also be obtained in the two scripts.

We can also visualize the media consumption globally (figure 8) from the eight countries to the top 50 domains with the most audience reach. The reason that we did not plot it (and also figure 5) in Sec 4.3 is we need the domain bias scores (in the US) for coloring, which is not available till this step. Heatmap is generated by `5_figure_8.py`. The script also saves the coloring values for domains that can be used for visualizing global media audience reach (`6_figure_5.py`), which corresponds to figure 5 in the paper.

## Section 5.4 Profiling Cross-Country COVID-19 News Consumption

In this section, we use our media bias scores to generate new findings through a country-centric view and a media-centric view. Codes can be found under `Sec_5_4_Profiling_Media_Consumption/`. Country-centric view (figure 9) and media-centric view (figure 10) can be generated by `1_figure_9.py` and `2_figure_10.py`, respectively. One can also modify `SELECTED_DOMAINS` in `utils/config.py` to inspect other domains as long as they are present in the extracted URLs.