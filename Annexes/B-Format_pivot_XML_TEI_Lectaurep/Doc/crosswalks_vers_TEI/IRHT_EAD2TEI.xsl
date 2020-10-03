<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns="http://www.tei-c.org/ns/1.0"
    xmlns:eac-cpf="urn:isbn:1-931666-33-4" exclude-result-prefixes="tei tmp eac-cpf"
    xmlns:tmp="http://www.oucs.ox.ac.uk/tmp">

    <xsl:output encoding="UTF-8" method="xml" indent="yes"/>

    <xsl:template match="/">
        <TEI xmlns="http://www.tei-c.org/ns/1.0">  <teiHeader>  <fileDesc>  <titleStmt> 
                            <title>Titre du document</title>  <author>  <persName/>  </author> 
                            <respStmt>  <persName/>  <resp>Conversion en format XML-TEI-P5</resp> 
                        </respStmt>  </titleStmt>  <publicationStmt>  <p>Projet St-Bertin</p> 
                            <publisher>  <orgName>Institut de recherche et d'histoire des textes,
                                CNRS</orgName>  </publisher>  <pubPlace>  <adress>40 avenue d’Iéna,
                                75116 Paris</adress>  </pubPlace>  <date>2015</date> 
                    </publicationStmt>  <sourceDesc>  <p>Document en format XML-EAD selon les normes
                            du Manuel de catalogage des  manuscrits médiévaux de la BnF</p> 
                    </sourceDesc>  </fileDesc>  <revisionDesc xmlns="http://www.tei-c.org/ns/1.0"> 
                        <change when="{format-date(current-date(),'[Y]-[M01]-[D01]')}"> File created
                    </change>  </revisionDesc>  </teiHeader>  <text>  <body>  <listBibl> 
                            <xsl:for-each select="//c[@otherlevel = 'notice']"> 
                            <!-- Sélection de chaque notice contenue dans le document -->  <msDesc> 
                                    <msIdentifier>  <settlement>Ville de conservation</settlement> 
                                        <repository>Etablissement de conservation</repository> 
                                        <idno>  <xsl:value-of
                                            select="did/unitid[@type = 'numéro_de_notice']"/>
                                        <!-- Cette commande va chercher la cote -->  </idno> 
                                </msIdentifier>  <msContents>  <xsl:if test="did/unittitle != ''"> 
                                        <!-- Ce test sert à exclure les contenus vides, il sera utilisé tout au long de la feuille de style  --> 
                                            <summary>  <xsl:value-of select="did/unittitle"/> 
                                            <!-- unittitle correspond au titre long -->  </summary> 
                                    </xsl:if>  <msItem>  <!-- boucle pour les 'controlaccess' --> 
                                            <xsl:for-each select="controlaccess"> 
                                            <!-- Le controlaccess correspond à la liste d'autorités du CCFr --> 
                                                <xsl:if test="persname != ''">  <author> 
                                                  <xsl:value-of select="persname"/> 
                                                  <!-- persname correspond à l'auteur --> 
                                                </author>  </xsl:if>  <xsl:if test="corpname != ''"
                                                >  <author>  <xsl:value-of select="corpname"/> 
                                                  <!-- corpname correspond à l'institution auteur de l'ouvrage  --> 
                                                </author>  </xsl:if>  <xsl:if test="title != ''"> 
                                                  <title>  <xsl:value-of select="title"/> 
                                                  <!-- title correspond au titre normalisé --> 
                                                </title>  </xsl:if>  <xsl:if test="subject != ''"> 
                                                  <note>  <xsl:value-of select="subject"/> 
                                                  <!-- subject correspond au sujet abordé dans l'ouvrage --> 
                                                </note>  </xsl:if>  <xsl:if test="name != ''"> 
                                                  <note>  <xsl:value-of select="name"/> 
                                                  <!-- name correspond à un contenu d'indexation indéfini --> 
                                                </note>  </xsl:if>  <xsl:if test="geogname != ''"> 
                                                  <note>  <geogName>  <xsl:value-of
                                                  select="geogname"/>  </geogName> 
                                                  <!-- geogname correspond à une zone géographique abordée dans l'ouvrage --> 
                                                </note>  </xsl:if>  </xsl:for-each>  <xsl:if
                                            test="did/langmaterial/language != ''">  <xsl:for-each
                                                select="did/langmaterial/language">  <textLang> 
                                                  <xsl:value-of select="."/> 
                                                  <!-- language correspond à la langue --> 
                                                </textLang>  </xsl:for-each>  </xsl:if>  <xsl:if
                                            test="scopecontent != ''">  <note>  <xsl:value-of
                                                  select="scopecontent"/> 
                                                <!-- scopecontent correspond au commentaire sur l'ouvrage --> 
                                            </note>  </xsl:if>  </msItem>  </msContents> 
                                    <physDesc>  <objectDesc form="codex">  <supportDesc>  <xsl:if
                                                test="did/physdesc/physfacet[@type = 'support'] != ''">
                                                <support>  <material>  <xsl:value-of
                                                  select="did/physdesc/physfacet[@type = 'support']"
                                                  />
                                                  </material>  </support>  </xsl:if>  <extent> 
                                                  <xsl:if test="did/physdesc/dimensions != ''"> 
                                                  <measure type="format">  <xsl:value-of
                                                  select="did/physdesc/dimensions"/>  </measure> 
                                                </xsl:if>  <xsl:if test="did/physdesc/extent != ''"
                                                  >  <measure type="composition">  <xsl:value-of
                                                  select="did/physdesc/extent"/>  </measure> 
                                                </xsl:if>  </extent>  </supportDesc>  </objectDesc> 
                                        <xsl:if test="did/physdesc/physfacet[@type = 'autre'] != ''"
                                        >  <decoDesc>  <decoNote>  <xsl:value-of
                                                  select="did/physdesc/physfacet[@type = 'autre']"/>
                                                <!-- autre contient différentes informations qu'il faudra diviser par la suite dans d'autres structures (comme le nombre de colonnes ou le type d'écriture). --> 
                                            </decoNote>  </decoDesc>  </xsl:if>  <xsl:if
                                        test="did/physdesc/physfacet[@type = 'reliure'] != ''"> 
                                            <bindingDesc>  <binding>  <p>  <xsl:value-of
                                                  select="did/physdesc/physfacet[@type = 'reliure']"
                                                  />
                                                </p>  </binding>  </bindingDesc>  </xsl:if> 
                                </physDesc>  <history>  <xsl:if test="did/unitdate != ''"> 
                                            <origin>  <origDate period="{did/unitdate/@era}"
                                                correp="{did/unitdate/@normal}"
                                                calendar="{did/unitdate/@calendar}">
                                                <xsl:value-of select="did/unitdate"/>  </origDate> 
                                        </origin>  </xsl:if>  <xsl:if
                                        test="note[@type = 'provenance'] != ''">  <provenance> 
                                                <xsl:value-of select="note[@type = 'provenance']"/> 
                                        </provenance>  </xsl:if>  </history>  <additional> 
                                        <adminInfo>  <note type="id-CGM" n="{./@id}"/> 
                                        <!-- Numéro d'identification dans la base du CCFr --> 
                                    </adminInfo>  </additional>   <xsl:if
                                    test=".//c[@otherlevel = 'sous-notice'] != ''"> 
                                    <!-- Le niveau "sous-notice" dans l'indentation du format EAD correspond au msPart de la TEI, le contenu est semblable au msDesc ci-dessus --> 
                                        <xsl:for-each select=".//c[@otherlevel = 'sous-notice']"> 
                                            <msPart n="{did/unitid[@type='division']}"> 
                                            <msIdentifier/>  <msContents>  <xsl:if
                                                  test="did/unittitle != ''">  <summary> 
                                                  <xsl:value-of select="did/unittitle"/> 
                                                  </summary>  </xsl:if>  <xsl:if
                                                  test="controlaccess != ''">  <msItem> 
                                                  <!-- boucle pour les 'controlaccess' --> 
                                                  <xsl:for-each select="controlaccess">  <xsl:if
                                                  test="persname != ''">  <author>  <xsl:value-of
                                                  select="persname"/>  </author>  </xsl:if>  <xsl:if
                                                  test="corpname != ''">  <author>  <xsl:value-of
                                                  select="corpname"/>  </author>  </xsl:if>  <xsl:if
                                                  test="title != ''">  <title>  <xsl:value-of
                                                  select="title"/>  </title>  </xsl:if>  <xsl:if
                                                  test="subject != ''">  <note>  <xsl:value-of
                                                  select="subject"/>  </note>  </xsl:if>  <xsl:if
                                                  test="name != ''">  <note>  <xsl:value-of
                                                  select="name"/>  </note>  </xsl:if>  <xsl:if
                                                  test="geogname != ''">  <note>  <geogName> 
                                                  <xsl:value-of select="geogname"/>  </geogName> 
                                                  </note>  </xsl:if>  </xsl:for-each>  <xsl:if
                                                  test="did/langmaterial/language != ''"> 
                                                  <textLang>  <xsl:value-of
                                                  select="did/langmaterial/language"/>  </textLang> 
                                                  </xsl:if>  <xsl:if test="scopecontent != ''"> 
                                                  <note>  <xsl:value-of select="scopecontent"/> 
                                                  </note>  </xsl:if>  </msItem>  </xsl:if> 
                                            </msContents>  <physDesc>  <xsl:if
                                                  test="did/physdesc/physfacet[@type = 'autre'] != ''">
                                                  <decoDesc>  <decoNote>  <xsl:apply-templates
                                                  select="did/physdesc/physfacet[@type = 'autre']"/>
                                                  </decoNote>  </decoDesc>  </xsl:if>  </physDesc> 
                                                <additional>  <adminInfo>  <note type="id-CGM"
                                                  n="{./@id}"/>  </adminInfo>  </additional> 
                                        </msPart>  </xsl:for-each>  </xsl:if>  </msDesc> 
                        </xsl:for-each>  </listBibl>  </body>  </text>  </TEI>  </xsl:template>
</xsl:stylesheet>
