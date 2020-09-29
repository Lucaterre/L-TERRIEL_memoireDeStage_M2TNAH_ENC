<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:ns="http://www.namescape.nl/"
    xmlns:alto="http://schema.ccs-gmbh.com/ALTO" xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="tei ns alto xsl xs"
    xpath-default-namespace="http://www.loc.gov/standards/alto/ns-v4#"
    xmlns="http://www.tei-c.org/ns/1.0" version="2.0">
    
    <!-- Script XSLT Lectaurep_Alto2TEI                                -->

    <!-- ***********************************************************     -->
    <!-- Version 1-2020-07-28                                            -->
    <!-- Cette feuille xsl a été développé dans le cadre du projet       -->
    <!-- LECTAUREP en lien avec les Archives Nationales/INRIA            -->
    <!-- *Crosswalk ALTO vers TEI                                        -->
    <!-- basé sur le script XSLT du Dutch Language Institute (INL) 
        -@OpenConvert Alto2tei adapté pour les besoins de Lectaurep      -->
    <!-- ***********************************************************     -->
    <!-- Author : Lucas Terriel                                          -->
    <!-- @Gitlab-INRIA/ALMANACH                                          -->
    <!-- ***********************************************************     -->
    <!-- Ce script est libre à la réutilisation selon les termes         -->
    <!-- de la Creative Commons Attribution license.                     -->
    <!-- ***********************************************************     -->

    <xsl:strip-space elements="*"/>
    <xsl:output method="xml" indent="yes"/>

    <xsl:variable name="DOCUMENT" select="collection('catalog_alto.xml')"/>
    <xsl:param name="scale">1</xsl:param>
    
    <!-- Ici on gère le framework TEI pour l'inclusion des données ALTO dans la partie <facsimile> et dans le <body> -->

    <xsl:template match="/">
        <!-- On créé un élément racine <div type='root'> pour faciliter la récupération lors de la transformation avec le préprocesseur Saxon -->
        <div type='root'>
        <facsimile>
            <xsl:for-each select="$DOCUMENT">
                <xsl:variable name="image_filename"
                    select="descendant::Description/sourceImageInformation/fileName/text()"/>
                <xsl:variable name="image_filename_without_extension"
                    select="substring-before($image_filename, '.jpg')"/>
                <xsl:variable name="i" select="position()"/>
                <surface>
                    <xsl:attribute name="facs">
                        <xsl:value-of select="concat('#', $image_filename_without_extension)"/>
                    </xsl:attribute>
                    <graphic>
                        <xsl:attribute name="url">
                            <xsl:value-of select="$image_filename"/>
                        </xsl:attribute>
                        <xsl:attribute name="xml:id">
                            <xsl:value-of select="$image_filename_without_extension"/>
                        </xsl:attribute>
                    </graphic>
                    <xsl:apply-templates select="./descendant::*[local-name() = 'Layout']"
                        mode="facsimile">
                        <xsl:with-param name="image_filename_without_extension"
                            select="$image_filename_without_extension" tunnel="yes"/>
                        <xsl:with-param name="position" select="$i" tunnel="yes"/>
                    </xsl:apply-templates>
                </surface>
            </xsl:for-each>
        </facsimile>
        <text>
            <body>
                <xsl:for-each select="$DOCUMENT">
                    <xsl:variable name="image_filename"
                        select="descendant::Description/sourceImageInformation/fileName/text()"/>
                    <xsl:variable name="image_filename_without_extension"
                        select="substring-before($image_filename, '.jpg')"/>
                    <xsl:variable name="i" select="position()"/>
                    <div>
                        <xsl:attribute name="type">
                            <xsl:text>surface</xsl:text>
                        </xsl:attribute>
                        <xsl:attribute name="facs">
                            <xsl:value-of select="concat('#', $image_filename_without_extension)"/>
                        </xsl:attribute>
                        <xsl:apply-templates select="descendant::*[local-name() = 'Layout']">
                            <xsl:with-param name="image_filename_without_extension"
                                select="$image_filename_without_extension" tunnel="yes"/>
                            <xsl:with-param name="position" select="$i" tunnel="yes"/>
                        </xsl:apply-templates>
                    </div>
                </xsl:for-each>
            </body>
        </text>
        </div>
    </xsl:template>
    
    <!-- Partie <body> -->

    <xsl:template match="descendant::*[local-name() = 'Layout']">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="*[local-name() = 'TextBlock']">
        <xsl:param name="image_filename_without_extension" tunnel="yes"/>
        <xsl:param name="position" tunnel="yes"/>
        <ab>
            <xsl:attribute name="facs">
                <xsl:value-of select="concat('#facblock_', $image_filename_without_extension)"/>
            </xsl:attribute>
            <xsl:attribute name="xml:id">
                <xsl:value-of select="concat('block_', $image_filename_without_extension)"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </ab>
    </xsl:template>

    <xsl:template match="*[local-name() = 'TextLine']">
        <xsl:param name="image_filename_without_extension" tunnel="yes"/>
        <xsl:apply-templates/>
        <lb>
            <xsl:attribute name="facs">
                <xsl:value-of
                    select="concat('#facline_', $image_filename_without_extension, '_', position())"
                />
            </xsl:attribute>
            <xsl:attribute name="xml:id">
                <xsl:value-of select="concat('esc_line_', $image_filename_without_extension, '_', position())"/>
            </xsl:attribute>
        </lb>
    </xsl:template>

    <xsl:template match="*[local-name() = 'SP']">
        <xsl:text> </xsl:text>
    </xsl:template>
    <!--
    <xsl:template match="*[local-name() = 'String'][@SUBS_TYPE = 'HypPart1']">
        <reg>
            <xsl:attribute name="orig"><xsl:value-of select="@CONTENT"/>|<xsl:variable name="s1"
                        ><xsl:value-of select="@CONTENT"/></xsl:variable><xsl:variable name="s2"
                        ><xsl:value-of select="@SUBS_CONTENT"/></xsl:variable><xsl:value-of
                    select="substring-after($s2, $s1)"/></xsl:attribute>
            <w>

                <xsl:value-of select="@SUBS_CONTENT"/>
            </w>
        </reg>
    </xsl:template>
-->
    <xsl:template match="*[local-name() = 'String'][@SUBS_TYPE = 'HypPart2']"/>

    <xsl:template match="*[local-name() = 'String']">
        <xsl:param name="image_filename_without_extension" tunnel="yes"/>
        <w>
            <xsl:attribute name="facs">
                <xsl:value-of select="concat('#facs_', $image_filename_without_extension, '_')"/>
                <xsl:number count="TextLine" level="multiple" format="1"/>
            </xsl:attribute>
            <xsl:attribute name="xml:id">
                <xsl:value-of select="concat('w_', $image_filename_without_extension, '_')"/>
                <xsl:number count="TextLine" level="multiple" format="1"/>
            </xsl:attribute>

            <xsl:value-of select="@CONTENT"/>
        </w>
    </xsl:template>
    
    <!-- Partie <facsimile> -->
    
    <!-- Fonction de calcul des coordonnées -->

    <xsl:function name="ns:scaleCoordinates">
        <!-- 
        Calcul des ulx, uly, lrx, et lry à partir des coordonnées XML ALTO
        
        PARAMS
        ======
        * value (int) : différentes coordonées
        -->
        <xsl:param name="value" as="xs:integer"/>
        <xsl:value-of select="$value * $scale"/>
    </xsl:function>
    
    <xsl:function name="ns:tokensCoordinatesWithSep">
        <!-- 
        formater les coordonées (pour polygones et baseline) présenté
        en liste points sous la forme de paires de points 
        
        PARAMS
        ======
        * points (list) : points de coordonées
        -->
        <xsl:param name="points"/>
        <xsl:value-of separator=" ">
            <xsl:for-each-group select="tokenize($points)" group-adjacent="(position() - 1) idiv 2">
                <xsl:sequence select="string-join(current-group(), ',')"/>
            </xsl:for-each-group>
        </xsl:value-of>
    </xsl:function>

    <xsl:template
        match="*[local-name() = 'PrintSpace' or local-name() = 'TextLine' or local-name() = 'TextBlock' or local-name() = 'String' or local-name() = 'Shape']"
        mode="facsimile">
        <xsl:param name="image_filename_without_extension" tunnel="yes"/>
        <xsl:param name="position" tunnel="yes"/>
        <xsl:param name="points_polygon" tunnel="yes"/>
        <zone>
            <xsl:attribute name="type">
                <xsl:value-of select="name(.)"/>
            </xsl:attribute>
            <xsl:if test="local-name() = 'PrintSpace'">
                <xsl:attribute name="xml:id">
                    <xsl:value-of select="concat('facPS_', $image_filename_without_extension)"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:if test="local-name() = 'TextLine'">
                <xsl:attribute name="xml:id">

                    <xsl:value-of
                        select="concat('facline_', $image_filename_without_extension, '_', position())"
                    />
                </xsl:attribute>
            </xsl:if>
            <xsl:if test="local-name() = 'TextBlock'">
                <xsl:attribute name="xml:id">
                    <xsl:value-of select="concat('facblock_', $image_filename_without_extension)"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:if test="local-name() = 'String'">
                <xsl:attribute name="xml:id">
                    <xsl:value-of select="concat('facs_', $image_filename_without_extension, '_')"/>
                    <xsl:number count="TextLine" level="multiple" format="1"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:if test="local-name() = 'Shape'">
                <xsl:variable name="points_polygon" select="./Polygon/@POINTS"/>
                <xsl:attribute name="type">
                    <xsl:text>Polygon</xsl:text>
                </xsl:attribute>
                <xsl:attribute name="points">
                    <xsl:value-of select="ns:tokensCoordinatesWithSep($points_polygon)"/>
                </xsl:attribute>
            </xsl:if>
            <xsl:if test="@HPOS and @WIDTH">
                <xsl:attribute name="ulx" select="ns:scaleCoordinates(xs:integer(@HPOS))"/>
                <xsl:attribute name="uly" select="ns:scaleCoordinates(xs:integer(@VPOS))"/>
                <xsl:attribute name="lrx"
                    select="ns:scaleCoordinates(xs:integer(@HPOS)) + ns:scaleCoordinates(xs:integer(@WIDTH))"/>
                <xsl:attribute name="lry"
                    select="ns:scaleCoordinates(xs:integer(@VPOS)) + ns:scaleCoordinates(xs:integer(@HEIGHT))"
                />
            </xsl:if>
            <xsl:apply-templates mode="#current"/>
        </zone>
    </xsl:template>
</xsl:stylesheet>
