package org.ceurws.reasoner;

import com.hp.hpl.jena.rdf.model.Model;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.rdf.model.NsIterator;
import com.hp.hpl.jena.reasoner.Reasoner;
import com.hp.hpl.jena.reasoner.ReasonerRegistry;
import com.hp.hpl.jena.vocabulary.ReasonerVocabulary;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import org.apache.jena.atlas.web.HttpException;
import org.apache.jena.riot.Lang;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.riot.RiotException;

public class Launcher {

    private static final String LANG = "TURTLE";

    public static void main(String[] args) {
        if (args.length > 2) {
            if (Files.exists(new File(args[0]).toPath())
                    && Files.exists(new File(args[1]).toPath())) {
                final Model dump = RDFDataMgr.loadModel(args[0]);
                final Model mappings = RDFDataMgr.loadModel(args[1]);

                final Reasoner reasoner = ReasonerRegistry.getOWLMicroReasoner();
//                reasoner.setParameter(ReasonerVocabulary.PROPsetRDFSLevel, 
//                        ReasonerVocabulary.RDFS_SIMPLE);
                Model infModel = ModelFactory.createInfModel(reasoner, mappings, dump);

                try (FileWriter writer = new FileWriter(args[2])) {
                    infModel.write(writer, LANG);
                } catch (IOException ex) {
                    ex.printStackTrace();
                }
            }
        } else {
            System.out.println("Provide an RDF dump, mapping file and path to the output file!");
        }
    }

    private static Model loadImports(final Model model) {
        Model newModel = ModelFactory.createDefaultModel().add(model);
        NsIterator iter = model.listNameSpaces();
        while (iter.hasNext()) {
            final String namespace = iter.next();
            try {
                newModel.add(RDFDataMgr.loadModel(namespace));
            } catch (RiotException ex) {
                System.out.print("Failed to determine the content type, trying RDF/XML...");
                newModel.add(RDFDataMgr.loadModel(namespace, Lang.RDFXML));
                System.out.println("Success!");
            } catch(HttpException ex) {
                System.out.println("Failed to load " + namespace + " ontology. Skipping!");
            }
        }
        return newModel;
    }

}
