<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns="http://www.tei-c.org/ns/1.0"
    xmlns:eac-cpf="urn:isbn:1-931666-33-4"
    xmlns:xs="http://www.w3.org/2002/ws/databinding/examples/6/09/"
    exclude-result-prefixes="tei xs eac-cpf">
    
    <!-- Script XSLT Lectaurep_EADEAC2TEI                                -->

    <!-- ***********************************************************     -->
    <!-- Version 1-2020-05-14                                            -->
    <!-- Cette feuille xsl a été développé dans le cadre du projet       -->
    <!-- LECTAUREP en lien avec les Archives Nationales/INRIA            -->
    <!-- *Crosswalk EAD-EAC vers TEI                                     -->
    <!-- ***********************************************************     -->
    <!-- Author : Lucas Terriel                                          -->
    <!-- @Gitlab-INRIA/ALMANACH                                          -->
    <!-- ***********************************************************     -->
    <!-- Ce script est libre à la réutilisation selon les termes         -->
    <!-- de la Creative Commons Attribution license.                     -->
    <!-- ***********************************************************     -->


    <xsl:strip-space elements="*"/>
    <xsl:output indent="yes" method="xml"/>

    <xsl:template match="/">


        <TEI xmlns="http://www.tei-c.org/ns/1.0">

            <!-- VARIABLES -->

            <!-- Warning : La fonction XPATH collection() appartient XSLT ET XPATH 2.0  -->

            <xsl:variable name="DOCUMENT" select="collection('catalog_ead_eac.xml')"/>
            <!-- pour Python et la lib lxml avec XSLT 1.0, hack de collection() possible :  document(document('catalogue-ead.xml')/*/doc/@href) -->

            <xsl:variable name="NOM_PRENOM_NOTAIRE"
                select="$DOCUMENT/descendant::archdesc/did/origination/persname/text()"/>
            
            <xsl:variable name="PERSNAME"
                select="$DOCUMENT//archdesc[@level = 'subfonds']/did/origination/persname/text()"/>

            <xsl:variable name="ETUDE"
                select="$DOCUMENT/descendant::archdesc/did/origination/corpname/text()"/>

            <xsl:variable name="EAD_FILENAMES">
                <xsl:for-each select="$DOCUMENT//eadid/text()">
                    <xsl:value-of select="concat(., ' - ')"/>
                </xsl:for-each>
            </xsl:variable>

            <xsl:variable name="IDENTIFIANT_MC-RE"
                select="$DOCUMENT//archdesc[@level = 'series']/did/unitid[@type = 'identifiant']"/>

            <xsl:variable name="ID_AUTO" select="generate-id(.)"/>

            <xsl:variable name="REPERTOIRES"
                select="$DOCUMENT//archdesc[@level = 'subfonds']/did/unitid"/>

            <xsl:variable name="PREMIER_REPERTOIRE" select="substring($REPERTOIRES, 38, 14)"/>

            <xsl:variable name="DERNIER_REPERTOIRE" select="substring($REPERTOIRES, 59, 14)"/>


            <teiHeader>
                <fileDesc>
                    <titleStmt>
                        <title>
                            <xsl:value-of
                                select="concat('Répertoire du notaire ', $NOM_PRENOM_NOTAIRE, ' - ', $ETUDE)"/>

                        </title>
                        <respStmt>
                            <persName>
                                <forename>
                                    <xsl:value-of
                                        select="substring-after($PERSNAME, ', ')"/>
                                </forename>
                                <!-- ** Nom notaire -->
                                <surname>
                                    <xsl:value-of
                                        select="substring-before($PERSNAME, ',')"/>
                                </surname>
                            </persName>
                            <resp>Conversion des instruments de recherche en EAD : <xsl:value-of
                                    select="$EAD_FILENAMES"/>, des fiches producteurs EAC, des
                                fichiers ALTO, et des métadonnées EXIF vers le format pivot TEI
                            </resp>
                        </respStmt>
                    </titleStmt>

                    <!-- PARTIE ADMINISTRATIVE -->

                    <publicationStmt>
                        <publisher>
                            <orgName>Minutier central des notaires parisiens, Archives nationales de
                                France</orgName>
                        </publisher>
                        <pubPlace>
                            <address>
                                <addrLine>11 rue des Quatre-Fils</addrLine>
                                <addrLine>75003 Paris</addrLine>
                                <addrLine>FRANCE</addrLine>
                            </address>
                        </pubPlace>
                        <availability status="free">
                            <!-- Voir pour changer le status -->
                            <p>Projet Lectaurep</p>
                            <!-- Ajout d'une licence à discuter -->
                        </availability>
                    </publicationStmt>

                    <!-- PARTIE CONCERNANT LES SOURCES REPERTOIRES - comprenant les liens vers les fiches producteurs EAC -->

                    <sourceDesc>

                        <msDesc xml:lang="fr">
                            <!-- générer un identifiant automatiquement : solution provisoire sinon envisager une fonction random et un xsl:param en python -->
                            <!-- ** Identification de la localisation des répertoires du notaires -->
                            <msIdentifier>

                                <country>France</country>
                                <settlement>Paris</settlement>
                                <institution>Archives nationales de France</institution>
                                <repository>Minutier central des notaires parisiens</repository>
                                <idno type="identifiant">
                                    <xsl:value-of select="$IDENTIFIANT_MC-RE"/>
                                </idno>

                            </msIdentifier>

                            <!-- ** Description du contenu des répertoires -->
                            <msContents>
                                <!-- *** Sommaire contenant les descriptions des images des répertoires et les métadonnées associées à celles-ci -->

                                <summary>
                                    <xsl:for-each
                                        select="$DOCUMENT//ancestor::archdesc[@level = 'series']//dsc/c">
                                        <xsl:variable name="ID_MCRE" select="@id"/>

                                        <list type="Répertoire">
                                            <xsl:attribute name="xml:id">
                                                <xsl:value-of select="$ID_MCRE"/>
                                            </xsl:attribute>
                                            <xsl:apply-templates select="did"/>


                                        </list>
                                    </xsl:for-each>

                                </summary>
                                <!-- *** Partie contenant les informations générales sur les répertoires -->
                                <msItemStruct xml:lang="fr">

                                    <locus from="{$PREMIER_REPERTOIRE}" to="{$DERNIER_REPERTOIRE}">
                                        <xsl:value-of
                                            select="substring-after($DOCUMENT//archdesc[@level = 'subfonds']/did/unitid, ',')"
                                        />
                                    </locus>
                                    <!-- ** Authentification du notaire -->
                                    <author>
                                        <!-- Ici on fait le lien avec la fiche producteur EAC -->
                                        <xsl:variable name="ID_EAD_NOTAIRE"
                                            select="$DOCUMENT//archdesc[@level = 'subfonds']/did/origination/persname/@authfilenumber"/>
                                        <persName source="{$ID_EAD_NOTAIRE}">
                                            <!-- ** Prénom notaire -->
                                            <forename>
                                                <xsl:value-of
                                                  select="substring-after($PERSNAME, ', ')"/>
                                            </forename>
                                            <!-- ** Nom notaire -->
                                            <surname>
                                                <xsl:value-of
                                                  select="substring-before($PERSNAME, ',')"/>
                                            </surname>
                                        </persName>
                                        <!-- *** Affiliation à une étude -->
                                        <xsl:variable name="ID_EAD_ETUDE"
                                            select="$DOCUMENT//archdesc[@level = 'subfonds']/did/origination/corpname/@authfilenumber"/>
                                        <orgName source="{$ID_EAD_ETUDE}">
                                            <xsl:value-of
                                                select="$DOCUMENT//archdesc[@level = 'subfonds']/did/origination/corpname/text()"
                                            />
                                        </orgName>
                                        <!-- *** Dates des répertoires -->
                                        <xsl:variable name="DATES_REPERTOIRES"
                                            select="$DOCUMENT//archdesc[@level = 'series']/did/unitdate/@normal"/>
                                        <date when-custom="{$DATES_REPERTOIRES}">
                                            <xsl:value-of
                                                select="$DOCUMENT//archdesc[@level = 'series']/did/unitdate"
                                            />
                                        </date>
                                    </author>
                                    <textLang mainLang="fr">français</textLang>

                                </msItemStruct>

                            </msContents>

                            <!-- Ici on gère les genreform auxquels sont rattachés les répertoires -->
                            <additional>
                                <surrogates>
                                    <xsl:variable name="ID_GENREFORM_SOURCE"
                                        select="$DOCUMENT//archdesc[@level = 'series']/controlaccess/genreform/@source"/>
                                    <bibl source="{$ID_GENREFORM_SOURCE}">

                                        <xsl:variable name="ID_GENREFORM_1"
                                            select="$DOCUMENT//archdesc[@level = 'series']/controlaccess/genreform/@authfilenumber"/>
                                        <title type="genreform">
                                            <xsl:attribute name="xml:id" select="$ID_GENREFORM_1"/>
                                            <xsl:value-of
                                                select="$DOCUMENT//archdesc[@level = 'series']/controlaccess/genreform/text()"
                                            />
                                        </title>
                                        <xsl:variable name="ID_GENREFORM_2"
                                            select="$DOCUMENT//archdesc[@level = 'series']/dsc/c[1]/controlaccess/genreform/@authfilenumber"/>
                                        <title type="genreform">
                                            <xsl:attribute name="xml:id" select="$ID_GENREFORM_2"/>
                                            <xsl:value-of
                                                select="$DOCUMENT//archdesc[@level = 'series']/dsc/c/controlaccess/genreform/text()"
                                            />
                                        </title>
                                    </bibl>
                                </surrogates>

                            </additional>

                        </msDesc>
                    </sourceDesc>
                </fileDesc>
                <encodingDesc>
                    <editorialDecl>
                        <p>1- ajout de la valeur "bytes values" pour les métadonnées EXIF dans xenodata lorsque la
                        valeur n'a pu être décoder en utf-8.</p>
                    </editorialDecl>
                </encodingDesc>
                <!--***********************************************************-->
                <!-- EMPLACEMENT POUR LES METADONNEES TECHNIQUES EXIF          -->
                <!-- DANS DES ARBRES <Xenodata> GENERES PAR UN SCRIPT PYTHON   -->
                <!--***********************************************************-->
                <revisionDesc>
                    <change when="{format-date(current-date(),'[Y]-[M01]-[D01]')}">File
                        created</change>
                </revisionDesc>
            </teiHeader>
            <!--***********************************************************-->
            <!-- EMPLACEMENT POUR DONNEES ALTO  (Cf.script Lectaurep_Alto2tei)
                 partie <facsimile>   -->
            <!--***********************************************************-->
            
               
                    <!--***********************************************************-->
                    <!-- EMPLACEMENT POUR DONNEES ALTO  (Cf.script Lectaurep_Alto2tei)
                         partie <body>  -->
                    <!--***********************************************************-->
                
            
        </TEI>
    </xsl:template>


    <!-- TEMPLATES ADD-ONS -->

    <!-- *Gestion contenu du <summary> -->
    <!-- niveau répertoire -->
    <!-- Possibilité de descendre plus bas pour le <desc> et le <note> dans le niveau de granularité notamment dans la description des colonnes
         via l'élément TEI <layoutDesc>, ou décrire les mains via l'élément TEI <scripDesc>-->

    <xsl:template match="did">
        <item>
            <idno type="cote-de-consultation">
                <xsl:value-of select="unitid[@type = 'cote-de-consultation']"/>
            </idno>
            <xsl:variable name="FROM_DATE_REPERTOIRE"
                select="substring-before(unitdate/@normal, ' /')"/>
            <xsl:variable name="TO_DATE_REPERTOIRE" select="substring-after(unitdate/@normal, '/ ')"/>
            <origDate from="{$FROM_DATE_REPERTOIRE}" to="{$TO_DATE_REPERTOIRE}">
                <xsl:value-of select="unitdate"/>
            </origDate>
            <!-- Ce test sert à exclure les contenus vides -->
            <xsl:if test="physdesc/extent != ''">
                <desc type="description_physique">
                    <xsl:value-of select="physdesc/extent"/>
                </desc>
            </xsl:if>
            <xsl:for-each select="following-sibling::scopecontent">
                <note type="description_diplomatique">
                    <xsl:value-of select="."/>
                </note>
            </xsl:for-each>
            <list type="contenu_Répertoire">
                <xsl:apply-templates select="following-sibling::c" mode="contenu_repertoire"/>
            </list>

        </item>
    </xsl:template>

    <!-- niveau contenu répertoire -->

    <xsl:template match="//c" mode="contenu_repertoire">
        <xsl:variable name="ID_TABLE-LISTE" select="@id"/>
        <item>
            <xsl:attribute name="xml:id" select="$ID_TABLE-LISTE"/>
            <xsl:if test="descendant::unitid[@type = 'pieces']">
                <idno type="pieces">
                    <xsl:value-of select="descendant::unitid[@type = 'pieces']/text()"/>
                </idno>
            </xsl:if>
            <xsl:if test="descendant::unitid[@type = 'identifiant']">
                <idno type="identifiant">
                    <xsl:value-of select="descendant::unitid[@type = 'identifiant']/text()"/>
                </idno>
            </xsl:if>
            <title>
                <xsl:value-of select="descendant::unittitle/text()"/>
            </title>
            <xsl:if test="descendant::physdesc/extent != ''">
                <material>
                    <xsl:value-of select="descendant::physdesc/extent/text()"/>
                </material>
            </xsl:if>
            <xsl:if test="descendant::scopecontent/p != ''">
                <note>
                    <xsl:value-of select="descendant::scopecontent/p/text()"/>
                </note>
            </xsl:if>
            <xsl:variable name="LINKS_IMAGES" select="//daogrp/daoloc/@href"/>
            <graphic>
                <xsl:attribute name="url">
                    <xsl:value-of select="$LINKS_IMAGES"/>
                </xsl:attribute>
            </graphic>

            <!--  concat(substring-before(//daogrp/daoloc/@href, '#'), '-',substring-after(//daogrp/daoloc/@href, '#'))-->
        </item>

    </xsl:template>



</xsl:stylesheet>
