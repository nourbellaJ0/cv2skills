#---------------------------------------------------------------------------------------
# Copyright (c) 2001-2023 by Apryse Software Inc. All Rights Reserved.
# Consult LICENSE.txt regarding license information.
#---------------------------------------------------------------------------------------

import site
site.addsitedir("../../../PDFNetC/Lib")
import sys
from PDFNetPython import *

sys.path.append("../../LicenseKey/PYTHON")
from LicenseKey import *

# Relative path to the folder containing the test files.
input_path = "../../TestFiles/"
output_path = "../../TestFiles/Output/"

#------------------------------------------------------------------------------
# The following sample illustrates how to use the PDF.Convert utility class
# to convert MS Office files to PDF and replace templated tags present in the document
# with content supplied via json
#
# For a detailed specification of the template format and supported features,
# see: https://docs.apryse.com/core/guides/generate-via-template/data-model/
#
# This conversion is performed entirely within the PDFNet and has *no*
# external or system dependencies -- Conversion results will be
# the same whether on Windows, Linux or Android.
#
# Please contact us if you have any questions.
#------------------------------------------------------------------------------

def main():
    # The first step in every application using PDFNet is to initialize the
    # library. The library is usually initialized only once, but calling
    # Initialize() multiple times is also fine.
    PDFNet.Initialize(LicenseKey)
    PDFNet.SetResourcesPath("../../../Resources")

    input_filename = "template.docx"
    output_filename = "SYH_Letter.pdf"

    json = """
    {
  "competences_techniques": [
    {
      "item": "C"
    },
    {
      "item": "C++"
    },
    {
      "item": "Cembarqué"
    },
    {
      "item": "JAVA"
    },
    {
      "item": "JavaScript"
    },
    {
      "item": "TypeScript"
    },
    {
      "item": "Html5"
    },
    {
      "item": "CSS3"
    },
    {
      "item": "Angular 19"
    },
    {
      "item": "React.js"
    },
    {
      "item": "Spring MVC"
    },
    {
      "item": "Spring Boot"
    },
    {
      "item": "Node.js"
    },
    {
      "item": "Bootstrap"
    },
    {
      "item": "docker"
    },
    {
      "item": "GIT"
    },
    {
      "item": "GITHUB"
    },
    {
      "item": "Visual Studio"
    },
    {
      "item": "WebStorm"
    },
    {
      "item": "IntelliJ"
    },
    {
      "item": "SQL"
    },
    {
      "item": "MySQL"
    }
  ],
  "experiences_cles_recentes": [
    {
      "annee": "Octobre 2022 –Aujourd’hui",
      "details": "Développement d'applications web avec Angular 19 et Spring Boot. Implémentation d'interfaces dynamiques et réactives en Angular 19. Animation et contribution active aux cérémonies Scrum.",
      "entreprise": "Sofrecom Tunisie",
      "intitule": "Ingénieur software"
    },
    {
      "annee": "Juin 2020–Octobre 2022",
      "details": "Angular 16: Realisation dudashboard “Spare panel” pour notre application depaiement banquaire “Spare”. Cyber security: Etablir lasecurité detransmission dedata entre lenavigateur et leserveur.",
      "entreprise": "Peak (Spare)",
      "intitule": "Développeur Front -end"
    }
  ],
  "experiences_professionnelles": [
    {
      "entreprise": "Sofrecom Tunisie",
      "missions": [
        {
          "item": "Développement d'applications web avec Angular 19 et Spring Boot"
        },
        {
          "item": "Implémentation d'interfaces dynamiques et réactives en Angular 19"
        },
        {
          "item": "Animation et contribution active aux cérémonies Scrum, incluant les Daily Stand -ups, Sprint Plannings, Rétrospectives et Démos, afin d'assurer une collaboration efficace, une amélioration continue et une livraison incrémentale de valeur."
        }
      ],
      "periode": "Octobre 2022 –Aujourd’hui",
      "poste": "Ingénieur software"
    },
    {
      "entreprise": "Peak (Spare)",
      "missions": [
        {
          "item": "Angular 16: Realisation dudashboard “Spare panel” pour notre application depaiement banquaire “Spare” (iOS etAndroid) sous Angular 12"
        },
        {
          "item": "Cyber security: Etablir lasecurité detransmission dedata entre lenavigateur et leserveur (browser -server) à travers la cryptographie Elliptic Curve Deffie -hellman (ECDH) et lasignature ECDSA"
        },
        {
          "item": "SDKs: Realisation detrois sdks desAPIdepaiement pour leslanguages javascript, java etphp"
        },
        {
          "item": "Slate: Creation dudocumentation “Spare docs” pour la description desAPI"
        },
        {
          "item": "Plugins: Realistaion dedeux plugins pour lamethode depaiement “Pay with Spare” avec Wordpress etmagento2"
        }
      ],
      "periode": "Juin 2020–Octobre 2022",
      "poste": "Développeur Front -end"
    },
    {
      "entreprise": "Sigma Industrie",
      "missions": [
        {
          "item": "Formations, certifications etréalisation des projets en développement web (Java / JavaScript) etC/C++"
        }
      ],
      "periode": "Juin 2018 -Mai2020\nMai 2017–juin 2018",
      "poste": "Formations, certifications etréalisation des projets en développement web (Java / JavaScript) etC/C++"
    },
    {
      "entreprise": "AURES AUTO Citroën",
      "missions": [
        {
          "item": "Réalisation d'un projet ensystèmes embarqués (automobile): système de détection de niveau deliquide derefroidissement pour levéhicule C4àbase d'une application Android"
        }
      ],
      "periode": "Février 2015–Juillet 2015",
      "poste": "Stage PFE"
    },
    {
      "entreprise": "TIS-circuit (Sagem)",
      "missions": [
        {
          "item": "Stage d'insertion"
        }
      ],
      "periode": "Juillet 2014",
      "poste": "Stage ingénieur"
    },
    {
      "entreprise": "Tunisie Télécom",
      "missions": [
        {
          "item": "Stage d'insertion"
        }
      ],
      "periode": "Juin 2013",
      "poste": "Stage d'insertion"
    }
  ],
  "formation_et_certifications": [
    {
      "annee": "2012 --2015",
      "diplome_certification": "Ingénieur enmécatronique IT",
      "etablissement": "Ecole nationale d'ingénieur deCarthage (ENICarthage)"
    },
    {
      "annee": "2010 -2012",
      "diplome_certification": "Etude préparatoire (spécialité: physique -chimie)",
      "etablissement": "Faculté dessciences de Monastir"
    },
    {
      "annee": "2010",
      "diplome_certification": "Baccalauréat Spécialité: mathématique ,Mention: Bien",
      "etablissement": "Lycée Nefta"
    }
  ],
  "informations_personnelles": {
    "adresse": "Cite Ettaamir 5-Ariana - Tunisie",
    "email": "yassin.bentaher@gmail.com",
    "nom": "BENTAHER",
    "prenom": "Yassin",
    "telephone": "+216 21885277"
  },
  "langues": [
    {
      "langue": "Anglais",
      "niveau": ""
    },
    {
      "langue": "français",
      "niveau": ""
    },
    {
      "langue": "Arabe",
      "niveau": ""
    }
  ],
  "methodologies": [
    {
      "item": "Scrum"
    }
  ],
  "projets_interessants": []
}
    """.format(input_path)

    # Create a TemplateDocument object from an input office file.
    template_doc = Convert.CreateOfficeTemplate(input_path + input_filename, None)

    # Fill the template with data from a JSON string, producing a PDF document.
    pdfdoc = template_doc.FillTemplateJson(json);

    # Save the PDF to a file.
    pdfdoc.Save(output_path + output_filename, SDFDoc.e_linearized)

    # And we're done!
    print("Saved " + output_filename )
    print("Done.")

if __name__ == '__main__':
    main()