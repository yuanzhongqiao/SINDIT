import datetime
from pathlib import Path  # Used for easier handling of auxiliary file's local path

import pyecma376_2  # The base library for Open Packaging Specifications. We will use the OPCCoreProperties class.
from basyx.aas import model
from basyx.aas.adapter import aasx

from typing import Dict, List
from graph_domain.main_digital_twin.AssetNode import AssetNodeDeep

# def _serialize_asset(asset: AssetNodeDeep):
#     pass


def serialize_to_aasx(
    aasx_file_path: str,
    assets: List[AssetNodeDeep],
    asset_similarities: Dict[str, float],
):
    aas_list: List[model.AssetAdministrationShell] = []
    object_store = model.DictObjectStore([])
    file_store = aasx.DictSupplementaryFileContainer()

    # Create the AAS objects
    for sindit_asset in assets:

        aas_asset = model.Asset(
            kind=model.AssetKind.INSTANCE,
            identification=model.Identifier(
                id_=sindit_asset.iri, id_type=model.IdentifierType.IRI
            ),
        )
        aas = model.AssetAdministrationShell(
            identification=model.Identifier(
                sindit_asset.iri + "_administration_shell", model.IdentifierType.IRI
            ),
            asset=model.AASReference.from_referable(aas_asset),
            submodel={},
        )

        aas_list.append(aas)
        object_store.add(aas_asset)
        object_store.add(aas)

    # Write the AAS objects to an AASX package
    with aasx.AASXWriter(aasx_file_path) as writer:
        for aas in aas_list:
            writer.write_aas(
                aas_id=aas.identification,
                object_store=object_store,
                file_store=file_store,
                submodel_split_parts=False,
            )
