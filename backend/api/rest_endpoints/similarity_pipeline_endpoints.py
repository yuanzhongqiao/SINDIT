from backend.api.api import app
import backend.api.python_endpoints.similarity_pipeline_endpoints as similarity_pipeline_endpoints


@app.get("/similarity_pipeline/status")
async def get_pipeline_status():
    """Combined status endpoint for the similarity pipeline.

    Returns:
        _type_: json
    """
    status_dict = similarity_pipeline_endpoints.get_pipeline_status()

    return status_dict


@app.post("/similarity_pipeline/time_series_feature_extraction")
async def post_time_series_feature_extraction():
    similarity_pipeline_endpoints.post_time_series_feature_extraction()


@app.post("/similarity_pipeline/time_series_dimensionality_reduction")
async def post_time_series_dimensionality_reduction():
    similarity_pipeline_endpoints.post_time_series_dimensionality_reduction()


@app.post("/similarity_pipeline/time_series_clustering")
async def post_time_series_clustering():
    similarity_pipeline_endpoints.post_time_series_clustering()


@app.post("/similarity_pipeline/text_keyphrase_extraction")
async def post_text_keyphrase_extraction():
    similarity_pipeline_endpoints.post_text_keyphrase_extraction()


@app.post("/similarity_pipeline/cad_analysis")
async def post_cad_analysis():
    similarity_pipeline_endpoints.post_cad_analysis()


@app.post("/similarity_pipeline/image_analysis")
async def post_image_analysis():
    similarity_pipeline_endpoints.post_image_analysis()


@app.post("/similarity_pipeline/asset_similarity")
async def post_asset_similarity():
    similarity_pipeline_endpoints.post_asset_similarity()
