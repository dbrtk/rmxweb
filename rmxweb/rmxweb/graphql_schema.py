import graphene

from container.queries import Query as CorpusQuery
from container.queries import (
    ContextPhrase, ContainerData, ContainerReady, ContainerStructure, DatasetReady,
    Doc, DocumentNode, Edge, Feat, FeatureContext, Features, FeatureNode,
    FeaturesWithDocs, FileText, Graph, GraphGenerate, TextInDataset, Texts,
    TxtDatum, Word
)
from container.mutations import Mutation as CorpusMutation
from data.queries import Data
from data.queries import Query as DataQuery


class RootQuery(CorpusQuery, DataQuery, graphene.ObjectType):

    pass


class Mutation(CorpusMutation, graphene.ObjectType):

    pass


schema = graphene.Schema(
    query=RootQuery,
    mutation=Mutation,
    types=[ContextPhrase, ContainerData, ContainerReady, ContainerStructure,
           DatasetReady, Doc, DocumentNode, Edge, Feat, FeatureContext,
           Features, FeatureNode, FeaturesWithDocs, FileText, Graph,
           GraphGenerate, TextInDataset, Texts, TxtDatum, Word, Data]
)
